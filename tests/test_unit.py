from main import get_treasures
from fastapi import HTTPException
import pytest

def test_get_treasure_raise_HTTPException():
    with pytest.raises(HTTPException):
        get_treasures(colour='noncolour')

