from sqlalchemy import text

from app.database.database import engine


try:

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version()")
        )

        print(
            "PostgreSQL connected successfully!"
        )

        print(
            result.fetchone()
        )

except Exception as error:

    print(
        "Database connection failed:"
    )

    print(error)