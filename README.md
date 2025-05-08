# tank-battle-grpc
Proyecto para la materia Computación en la Nube que consiste en un juego multijugador usando gRPC y python


go get google.golang.org/grpc

Compilar a python
`pip install grpcio-tools`

`python -m grpc_tools.protoc -I=server --python_out=server/game --grpc_python_out=server/game server/game.proto`
ajustar el .py generado colocando
from . import game_pb2 as game__pb2
protoc --go_out=. --go-grpc_out=. server/game.proto




Ir a la carpeta del servidor
`cd server`

Iniciar servidor
`go run server.go`

Iniciar clientes
`go run client.go`


