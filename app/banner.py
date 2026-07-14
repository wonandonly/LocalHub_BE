from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import random

router = APIRouter(prefix="/api/banner", tags=["Banner"])

DATA_DIR = Path(__file__).parent.parent / "data"


# 각 배너 그룹
VIEW_TYPES = {"쇼핑", "숙박", "여행코스"}
PLAY_TYPES = {"관광지", "레포츠", "문화시설", "축제공연행사"}


def load_banner_data():
    banners = {
        "view": [],
        "play": []
    }

    for json_file in DATA_DIR.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        content_type = data.get("contentType")

        for item in data.get("items", []):

            # 이미지 없는 데이터 제외
            if not item.get("firstimage") or not item.get("firstimage2"):
                continue

            banner = {
                "contentId": item["contentid"],
                "image": item["firstimage"],
                "title": item["title"],
                "address": item["addr1"],
            }

            if content_type in VIEW_TYPES:
                banners["view"].append(banner)

            elif content_type in PLAY_TYPES:
                banners["play"].append(banner)

    return banners


# 서버 시작 시 한 번만 로드
BANNERS = load_banner_data()


@router.get("/{category}")
def get_random_banner(category: str):
    """
    category
    - view : 쇼핑 / 숙박 / 여행코스
    - play : 관광지 / 레포츠 / 문화시설 / 축제공연행사
    """

    if category not in BANNERS:
        raise HTTPException(status_code=400, detail="category는 view 또는 play만 가능합니다.")

    if not BANNERS[category]:
        raise HTTPException(status_code=404, detail="배너 데이터가 없습니다.")

    return random.choice(BANNERS[category])

#볼거리 배너 GET /banner/view 즐길거리 배너 GET /banner/play

@router.get("/detail/{content_id}")
def get_detail(content_id: str):

    for json_file in DATA_DIR.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data.get("items", []):

            if item["contentid"] == content_id:

                return {
                    "contentId": item["contentid"],
                    "title": item["title"],
                    "image": item["firstimage"],
                    "image2": item["firstimage2"],
                    "address": item["addr1"],
                    "zipcode": item["zipcode"]
                }

    raise HTTPException(
        status_code=404,
        detail="관광지를 찾을 수 없습니다."
    )