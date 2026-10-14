from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Galaxy Atlas", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class Region(str, Enum):
    outer = "outer"
    core = "core"
    unknown = "unknown"


class Planet(BaseModel):
    id: str
    name: str
    region: Region
    terrain: str
    description: str
    color: str
    moons: int


PLANETS = [
    Planet(id="tatooine", name="Татуин", region=Region.outer, terrain="Пустыня",
           description="Два солнца, бескрайние дюны и начало большого пути. Родной мир Люка Скайуокера.", color="sand", moons=3),
    Planet(id="hoth", name="Хот", region=Region.outer, terrain="Ледяной мир",
           description="Тихая ледяная пустыня, скрывавшая базу «Эхо» и надежду Альянса повстанцев.", color="ice", moons=3),
    Planet(id="endor", name="Эндор", region=Region.outer, terrain="Лесная луна",
           description="Лесная луна, дом эвоков и место решающей битвы против второй Звезды Смерти.", color="forest", moons=0),
    Planet(id="coruscant", name="Корусант", region=Region.core, terrain="Город-планета",
           description="Тысячи уровней города, огни воздушных трасс и древние залы Храма джедаев.", color="city", moons=4),
    Planet(id="dagobah", name="Дагоба", region=Region.outer, terrain="Болота",
           description="Туман, древние деревья и убежище Йоды. Здесь тишина учит слышать Силу.", color="swamp", moons=1),
    Planet(id="ahch-to", name="Ак-То", region=Region.unknown, terrain="Океан и острова",
           description="Скалистые острова посреди океана и первый храм ордена джедаев.", color="ocean", moons=2),
    Planet(id="kamino", name="Камино", region=Region.outer, terrain="Океан и штормы",
           description="Бесконечный океан, грозовое небо и город Типока на высоких опорах. Мир создателей армии клонов.", color="storm", moons=3),
]


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "service": "galaxy-atlas"}


@app.get("/api/planets", response_model=list[Planet])
def planets(q: str = Query(default="", max_length=100), region: Region | None = None):
    query = q.strip().casefold()
    return [p for p in PLANETS
            if (region is None or p.region == region)
            and (not query or query in f"{p.name} {p.id} {p.terrain}".casefold())]


@app.get("/api/planets/{planet_id}", response_model=Planet)
def planet(planet_id: str):
    for item in PLANETS:
        if item.id == planet_id:
            return item
    raise HTTPException(status_code=404, detail="Планета не найдена")
