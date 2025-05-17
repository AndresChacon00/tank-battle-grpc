# tank-battle-grpc
Proyecto para la materia Computación en la Nube que consiste en un juego multijugador usando gRPC y python




Compilar cambios del game.proto
1.Verificar que las librerias esten instaladas
`pip install grpcio-tools`
`go get google.golang.org/grpc`

`go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest`
`go install google.golang.org/protobuf/cmd/protoc-gen-go@latest`

2.Ir a la ruta del servidor y ejecutar el comando para generar el codigo grpc
`cd server`
`protoc --go_out=. --go-grpc_out=. game.proto`

3.Ir al directorio raiz y ejecutar el comando para generar el codigo grpc python
`cd ..`
`python -m grpc_tools.protoc -I=server --python_out=server/game --grpc_python_out=server/game server/game.proto`

4. Ajustar el código generado game_pb2_grpc.py ya que tiene un error
En la linea 6:
from . import game_pb2 as game__pb2

5. Copiar la carpeta game y pegar en el cliente también.




Ir a la carpeta del servidor
`cd server`

Iniciar servidor
`go run server.go`

Iniciar clientes
`go run client.go`


