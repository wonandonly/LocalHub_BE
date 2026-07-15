from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(prefix="/api/place", tags=["Place"])

DATA_DIR = Path(__file__).parent.parent / "data"

# URL 파라미터 -> 파일명 매핑
FILE_MAP = {
    "tour": "서울_관광지.json",
    "culture": "서울_문화시설.json",
    "healing": "서울_레포츠.json",
    "shopping": "서울_쇼핑.json",
    "travel": "서울_여행코스.json",
    "festival": "서울_축제공연행사.json",
}

def load_places():
    places = {}

    for key, filename in FILE_MAP.items():
        file_path = DATA_DIR / filename

        if not file_path.exists():
            places[key] = []
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        places[key] = [
            {
                "contentId": item["contentid"],
                "image": item["firstimage"],
                "title": item["title"],
                "address": item["addr1"],
                "mapx": item["mapx"],
                "mapy": item["mapy"],
            }
            for item in data.get("items", [])
            if item.get("firstimage")
        ]

    return places


# 서버 시작 시 한 번만 로드
PLACES = load_places()


@router.get("/{content_type}")
def get_places(content_type: str):
    """
    tour
    culture
    healing
    shopping
    travel
    festival
    """

    if content_type not in PLACES:
        raise HTTPException(
            status_code=404,
            detail="지원하지 않는 콘텐츠 타입입니다."
        )

    return PLACES[content_type]