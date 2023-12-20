from django.core.exceptions import ValidationError


def validate_file_size(file):
    max_file_size_in_KB = 500
    if file.size > max_file_size_in_KB * 1024:
        raise ValidationError(
            f"Files cannot be greater than {max_file_size_in_KB}KB!")
