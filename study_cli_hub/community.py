# community.py - GitHub Discussions-backed feed, comments, and async chat.
#
# Why Discussions instead of git files: any GitHub account can post/comment on
# a public repo's Discussions without being a collaborator, and there's no
# file to merge - GitHub's API is the source of truth. That gets us
# permission-less access and conflict-free writes for free, with no server
# of our own to run.
import requests

from study_cli_hub import github_auth

GRAPHQL_URL = "https://api.github.com/graphql"
REPO_OWNER = "govindmehta15"
REPO_NAME = "study-cli-hub"

FEED_PREFIX = "[feed] "
CHAT_PREFIX = "[chat] "

REACTION_EMOJI = {
    "THUMBS_UP": "👍", "THUMBS_DOWN": "👎", "LAUGH": "😄", "HOORAY": "🎉",
    "CONFUSED": "😕", "HEART": "❤️", "ROCKET": "🚀", "EYES": "👀",
}
REACTION_ALIASES = {
    "thumbsup": "THUMBS_UP", "+1": "THUMBS_UP", "up": "THUMBS_UP", "like": "THUMBS_UP",
    "thumbsdown": "THUMBS_DOWN", "-1": "THUMBS_DOWN", "down": "THUMBS_DOWN",
    "laugh": "LAUGH", "haha": "LAUGH",
    "hooray": "HOORAY", "tada": "HOORAY", "party": "HOORAY",
    "confused": "CONFUSED",
    "heart": "HEART", "love": "HEART",
    "rocket": "ROCKET",
    "eyes": "EYES", "watching": "EYES",
}

_repo_cache = {}


def _headers():
    token_data = github_auth.load_token()
    if not token_data:
        return None
    return {"Authorization": f"bearer {token_data['access_token']}"}


def is_logged_in():
    return github_auth.load_token() is not None


def current_username():
    token_data = github_auth.load_token()
    return token_data.get("login") if token_data else None


def _graphql(query, variables=None):
    headers = _headers()
    if not headers:
        return None, "Not logged in. Run /login first."
    try:
        resp = requests.post(
            GRAPHQL_URL, json={"query": query, "variables": variables or {}}, headers=headers, timeout=20
        )
        data = resp.json()
    except requests.RequestException as e:
        return None, f"Could not reach GitHub: {e}"
    if "errors" in data and data["errors"]:
        return None, "; ".join(e.get("message", str(e)) for e in data["errors"])
    return data.get("data"), None


def _repo_info(force=False):
    if not force and "id" in _repo_cache:
        return _repo_cache, None
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
        hasDiscussionsEnabled
        discussionCategories(first: 20) { nodes { id name } }
      }
    }
    """
    data, err = _graphql(query, {"owner": REPO_OWNER, "name": REPO_NAME})
    if err:
        return None, err
    repo = data["repository"]
    if not repo["hasDiscussionsEnabled"]:
        return None, (
            "Discussions aren't enabled on this repo yet. "
            "A maintainer needs to turn it on in Settings > General > Features."
        )
    _repo_cache["id"] = repo["id"]
    _repo_cache["categories"] = {c["name"]: c["id"] for c in repo["discussionCategories"]["nodes"]}
    return _repo_cache, None


def _category_id(preferred_names):
    info, err = _repo_info()
    if err:
        return None, err
    categories = info["categories"]
    for name in preferred_names:
        if name in categories:
            return categories[name], None
    if categories:
        return next(iter(categories.values())), None
    return None, "No discussion category available to post into."


def _create_discussion(title, body, preferred_categories):
    info, err = _repo_info()
    if err:
        return None, err
    cat_id, err = _category_id(preferred_categories)
    if err:
        return None, err
    mutation = """
    mutation($repoId: ID!, $catId: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {repositoryId: $repoId, categoryId: $catId, title: $title, body: $body}) {
        discussion { id number title url }
      }
    }
    """
    data, err = _graphql(mutation, {"repoId": info["id"], "catId": cat_id, "title": title, "body": body})
    if err:
        return None, err
    return data["createDiscussion"]["discussion"], None


def _add_comment(discussion_id, body):
    mutation = """
    mutation($discussionId: ID!, $body: String!) {
      addDiscussionComment(input: {discussionId: $discussionId, body: $body}) {
        comment { id body createdAt author { login } }
      }
    }
    """
    data, err = _graphql(mutation, {"discussionId": discussion_id, "body": body})
    if err:
        return None, err
    return data["addDiscussionComment"]["comment"], None


def _list_discussions(search_query, limit=20):
    query = """
    query($q: String!, $n: Int!) {
      search(query: $q, type: DISCUSSION, first: $n) {
        nodes {
          ... on Discussion {
            id
            number
            title
            body
            url
            createdAt
            author { login }
            reactionGroups { content viewerHasReacted reactors { totalCount } }
            comments(first: 50) {
              totalCount
              nodes {
                id body createdAt author { login }
                reactionGroups { content viewerHasReacted reactors { totalCount } }
              }
            }
          }
        }
      }
    }
    """
    data, err = _graphql(query, {"q": search_query, "n": limit})
    if err:
        return None, err
    return data["search"]["nodes"], None


def normalize_reaction(name):
    """'heart', 'HEART', ':heart:', '+1' -> 'HEART'/'THUMBS_UP'; None if unknown."""
    key = name.strip().lower().strip(":")
    if key.upper() in REACTION_EMOJI:
        return key.upper()
    return REACTION_ALIASES.get(key)


def add_reaction(subject_id, content):
    mutation = """
    mutation($id: ID!, $content: ReactionContent!) {
      addReaction(input: {subjectId: $id, content: $content}) {
        reaction { id content }
      }
    }
    """
    data, err = _graphql(mutation, {"id": subject_id, "content": content})
    if err:
        return None, err
    return data["addReaction"]["reaction"], None


def remove_reaction(subject_id, content):
    mutation = """
    mutation($id: ID!, $content: ReactionContent!) {
      removeReaction(input: {subjectId: $id, content: $content}) {
        reaction { id content }
      }
    }
    """
    data, err = _graphql(mutation, {"id": subject_id, "content": content})
    if err:
        return None, err
    return data["removeReaction"]["reaction"], None


def toggle_reaction(subject_id, content, currently_reacted):
    return remove_reaction(subject_id, content) if currently_reacted else add_reaction(subject_id, content)


def has_reacted(item, content):
    return any(g["content"] == content and g["viewerHasReacted"] for g in item.get("reactionGroups") or [])


# ---------------------------------------------------------------- Feed


def post_to_feed(text):
    title = f"{FEED_PREFIX}{text.strip()[:60]}"
    return _create_discussion(title, text, ["Feed", "Announcements", "General"])


def list_feed(limit=20):
    nodes, err = _list_discussions(f"repo:{REPO_OWNER}/{REPO_NAME} in:title \"{FEED_PREFIX}\"", limit=limit)
    if err:
        return None, err
    return [n for n in nodes if n["title"].startswith(FEED_PREFIX)], None


def comment_on_feed_post(discussion_id, text):
    return _add_comment(discussion_id, text)


# ---------------------------------------------------------------- Explore other users


def list_feed_by_author(username, limit=20):
    nodes, err = _list_discussions(
        f"repo:{REPO_OWNER}/{REPO_NAME} in:title \"{FEED_PREFIX}\" author:{username}", limit=limit
    )
    if err:
        return None, err
    return [n for n in nodes if n["title"].startswith(FEED_PREFIX)], None


# ---------------------------------------------------------------- Async chat


def _chat_title(user_a, user_b):
    pair = "-".join(sorted([user_a.lower(), user_b.lower()]))
    return f"{CHAT_PREFIX}{pair}"


def get_or_create_chat_thread(user_a, user_b):
    title = _chat_title(user_a, user_b)
    nodes, err = _list_discussions(f"repo:{REPO_OWNER}/{REPO_NAME} in:title \"{title}\"", limit=5)
    if err:
        return None, err
    for node in nodes:
        if node["title"] == title:
            return node, None

    discussion, err = _create_discussion(
        title,
        f"Async chat thread between @{user_a} and @{user_b}. Messages sync whenever either of you runs /chat.",
        ["Chat", "General"],
    )
    if err:
        return None, err
    discussion["comments"] = {"totalCount": 0, "nodes": []}
    discussion["reactionGroups"] = []
    return discussion, None


def send_chat_message(discussion_id, text):
    return _add_comment(discussion_id, text)


def list_my_chat_threads(username, limit=50):
    """All chat threads this user is a party to. _chat_title() always sorts
    the pair alphabetically into the title, so a plain substring search for
    the username inside '[chat] ...' titles finds every thread involving them."""
    nodes, err = _list_discussions(
        f'repo:{REPO_OWNER}/{REPO_NAME} in:title "{CHAT_PREFIX}" {username}', limit=limit
    )
    if err:
        return None, err
    return [
        n for n in nodes
        if n["title"].startswith(CHAT_PREFIX) and username.lower() in n["title"].lower()
    ], None
