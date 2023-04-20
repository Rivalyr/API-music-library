from fastapi import FastAPI, Body, HTTPException
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from pydantic import BaseModel
from db.main import db


# Modelo a seguir cuando se suba una cancion
class Songinfo(BaseModel):
    title: str = None
    artist: str = None
    url: str = None
    # Se agrega la fecha de creacion automaticamente. Y se veria tal que asi "Friday 10. 03/2023"
    added: datetime = None


descripcion = "API creada para almacenar mi música con links directos a ellos, para acceder más rápido con la información más precisa y" \
              " buscarla en distintas plataformas"
app = FastAPI(
    title='RivaMusic',
    description=descripcion,
    docs_url='/docum'
)


@app.on_event("startup")
async def dbcon():
    print('Base de datos cargada y colección seleccionada')


@app.get("/songs")
async def main():
    # Lista falsa. Para darles formato basicamente
    songfkdb = []
    # Busca todos los objetos de la base de datos
    songsdb = db["Songs"].find()
    # Recorre con un bucle asincrono todos los objetos de la db
    async for songinfo in songsdb:
        # Elimina el '_id' basicamente por tema visual. Se ve feo tener otro diccionario dentro. Pero perfectamente se podria mostrar con ↙
        # songinfo["_id"] = str(songinfo["_id"])
        songinfo.pop('_id')
        songfkdb.append(songinfo)
    print(songfkdb)
    return songfkdb


@app.post('/upload/{song_id}')
async def uploadinfo(song_id: str,
                     song: Songinfo = Body(example={
                         "title": "Rick Astley - Never Gonna Give You Up",
                         "artist": "Rick Astley",
                         "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                         "added": datetime.now()
                     }
                     )):
    # ->                       codigo                       <-

    song.added = song.added.strftime("%A %d. %m/%Y")  # Cambia la fecha a string y le da un formato

    # Se transforma a un formato compatible con json para pasarlo a la db
    jsonparsedinfo = jsonable_encoder(song.dict())
    dbsongresult = await db["Songs"].insert_one({song_id: jsonparsedinfo})
    if dbsongresult:
        return jsonparsedinfo# "Canción agregada con éxito"
    else:
        raise HTTPException(status_code=404, detail='Fallo al intentar subir la canción. ¡No toques la fecha!')


@app.put("/update/{song_id}")
async def updatesong(song_id: str, songmod: Songinfo):
    songmod.added = songmod.added.strftime("%A %d. %m/%Y")
    updatejson = jsonable_encoder(songmod.dict())
    dbmodresult = await db["Songs"].find_one_and_update({song_id: {"$exists": True}}, {"$set": {song_id: updatejson}})
    if dbmodresult:
        return "Datos de canción modificados con éxito"
    else:
        raise HTTPException(status_code=404, detail='Los datos de la canción no han sido modificados. ¡No toques la fecha!')


@app.delete("/delete/{song_id}")
async def updatesong(song_id: str):
    # Si esa 'song_id' existe, la elimina directamente
    songdel = await db["Songs"].find_one_and_delete({song_id: {"$exists": True}})
    if songdel:
        return 'Canción eliminada con éxito'
    else:
        raise HTTPException(status_code=404, detail='¡Fallo al eliminar la canción, por favor revisa el ID!')
