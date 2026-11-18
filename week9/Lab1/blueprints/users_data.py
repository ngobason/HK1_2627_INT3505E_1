USERS = {
    1: {
        "first_name": "Van",
        "last_name": "Nguyen",
        "email": "a@vnu.vn"
    },
    2: {
        "first_name": "Trang",
        "last_name": "Tran",
        "email": "b@vnu.vn"
    }
}

def get_user(uid):
    return USERS.get(uid)
