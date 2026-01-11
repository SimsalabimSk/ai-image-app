from __future__ import annotations

import datetime as dt

from sqlalchemy.orm import Session

from packages.common.db import get_session
from packages.common.orm_models import Project, User


def main() -> None:
    session_gen = get_session()
    session: Session = next(session_gen)
    try:
        # idempotent seed
        user = session.get(User, "user_demo")
        if user is None:
            user = User(user_id="user_demo", email="demo@example.com", created_at=dt.datetime.utcnow())
            session.add(user)

        project = session.get(Project, "proj_demo")
        if project is None:
            project = Project(project_id="proj_demo", user_id="user_demo", name="Demo Project", created_at=dt.datetime.utcnow())
            session.add(project)

        session.commit()
        print("Seed OK: user_demo, proj_demo")
    finally:
        session.close()
        try:
            session_gen.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
