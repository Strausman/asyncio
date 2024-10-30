import asyncio
import datetime
import logging

import aiohttp
from more_itertools import chunked

from models import DbSession, SwapiPeople, close_orm, init_orm

MAX_CHUNK = 5

# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def get_resource_name(http_session, url):
    async with http_session.get(url) as response:
        resource_data = await response.json()
        return resource_data.get("title", resource_data.get("name", "Unknown"))  # Обработка случаев, когда 'name' отсутствует


async def get_people(http_session, people_id):
    try:
        response = await http_session.get(f"https://swapi.dev/api/people/{people_id}/")
        person_data = await response.json()

        if 'name' not in person_data:
            logging.error(f"Error: 'name' not found in data for person_id {people_id}: {person_data}")
            return None  # Пропустить запись, если 'name' отсутствует

        # Получаем названия фильмов
        films = await asyncio.gather(*[get_resource_name(http_session, url) for url in person_data.get('films', [])])

        # Получаем названия видов
        species = await asyncio.gather(*[get_resource_name(http_session, url) for url in person_data.get('species', [])])

        # Получаем названия кораблей
        starships = await asyncio.gather(*[get_resource_name(http_session, url) for url in person_data.get('starships', [])])

        # Получаем названия транспорта
        vehicles = await asyncio.gather(*[get_resource_name(http_session, url) for url in person_data.get('vehicles', [])])

        # Возвращаем объект ORM модели
        return SwapiPeople(
            id=people_id,
            name=person_data['name'],
            birth_year=person_data.get('birth_year', 'Unknown'),
            eye_color=person_data.get('eye_color', 'Unknown'),
            films=', '.join(films),
            gender=person_data.get('gender', 'Unknown'),
            hair_color=person_data.get('hair_color', 'Unknown'),
            height=person_data.get('height', 'Unknown'),
            homeworld=await get_resource_name(http_session, person_data.get('homeworld', '')),
            mass=person_data.get('mass', 'Unknown'),
            skin_color=person_data.get('skin_color', 'Unknown'),
            species=', '.join(species),
            starships=', '.join(starships),
            vehicles=', '.join(vehicles),
            url=person_data.get('url', 'Unknown'),
            created=person_data.get('created', 'Unknown'),
            edited=person_data.get('edited', 'Unknown'),
        )

    except aiohttp.ClientError as e:
        logging.error(f"Request failed for person_id {people_id}: {e}")
        return None

    except Exception as e:
        logging.error(f"Error occurred for person_id {people_id}: {e}")
        return None


async def insert_people(people_objects):
    try:
        async with DbSession() as session:
            session.add_all(people_objects)
            await session.commit()

    except Exception as e:
        logging.error(f"Error occurred while inserting people: {e}")


async def main():
    await init_orm()

    async with aiohttp.ClientSession() as http_session:
        tasks = []
        for chunk_i in chunked(range(1, 100), MAX_CHUNK):
            coros = [get_people(http_session, i) for i in chunk_i]
            result = await asyncio.gather(*coros)
            valid_results = [r for r in result if r]  # Исключаем None
            task = asyncio.create_task(insert_people(valid_results))
            tasks.append(task)
        await asyncio.gather(*tasks)

    await close_orm()


start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)