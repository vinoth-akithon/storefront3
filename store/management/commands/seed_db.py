import os
from pathlib import Path
from typing import Any
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Populate the datbase with collections and products"

    def handle(self, *args: Any, **options: Any) -> str | None:
        print("Populating the database...")
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "seed.sql")
        sql = Path(file_path).read_text()

        with connection.cursor() as cursor:
            cursor.execute(sql)
            print("Done")
