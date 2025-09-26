# Instagram Followers/Followings Audit

Audit an Instagram account’s **followers** and **followings** using private web endpoints, with safe pagination and tidy outputs:

* Markdown summary with tables
* CSV datasets (followers, followings, mutuals, not-following-back, etc.)
* JSON snapshot with counts, sets, and raw nodes
* Console summary

## Author

**Mathieu Renaud**
DevOps / Security / Web Engineer

* 📧 [mathieu.renaud29@gmail.com](mailto:mathieu.renaud29@gmail.com)
* 🌐 [https://mathieurenaud.fr](https://mathieurenaud.fr)
* 🔗 [https://www.linkedin.com/in/mathieu-renaud-inge/](https://www.linkedin.com/in/mathieu-renaud-inge/)

---

## Requirements

* Python 3.10+
* A valid, logged-in Instagram session (to provide cookies)

---

## Installation

```bash
# 1) Clone the repo
git clone https://github.com/Equinoxis/Instagram-Followers-Audit.git
cd Instagram-Followers-Audit

# 2) (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt
```

---

## Configuration

### Cookies

Create a `cookies.json` file in the project root with the **three required** keys from a logged-in Instagram session:

```json
{
  "csrftoken": "YOUR_CSRF_TOKEN",
  "ds_user_id": "YOUR_USER_ID",
  "sessionid": "YOUR_SESSION_ID"
}
```

**How to get these quickly (one option):**

1. Log into Instagram on the web.
2. Open DevTools → Application/Storage → Cookies for `https://www.instagram.com/`.
3. Copy values for `csrftoken`, `ds_user_id`, `sessionid` into `cookies.json`.

> If any key is missing, the program will fail fast with a clear error.

## Usage

```bash
python main.py --username <account_name> --cookies cookies.json
```

## Outputs

Inside `./out/<account_name>/`:

* **summary.md**
  Readable Markdown report with a Summary table and sections for:

  * Mutuals
  * I don’t follow back
  * Not following back

* **snapshot.json**
  Machine-readable snapshot with:

  * `counts`: totals per set
  * `sets`: usernames grouped by category
  * `followers`, `followings`: normalized node lists (username, full\_name, verified, private, pk, profile\_pic\_url)
  * `generated_utc`, `username`

* **CSV files**

  * `followers.csv`, `followings.csv` (full lists with metadata)
  * `mutuals.csv`
  * `i_dont_follow_back.csv`
  * `not_following_back.csv` (**unverified only**)
  * `verified_not_following_back.csv`

* **Non\_Abonne\_En\_Retour\_De\_\<account\_name>.txt**
  Compact legacy text overview.
