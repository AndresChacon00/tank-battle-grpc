// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.5.1
// - protoc             v6.31.0
// source: game.proto

package game

import (
	context "context"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
)

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
// Requires gRPC-Go v1.64.0 or later.
const _ = grpc.SupportPackageIsVersion9

const (
	GameService_UpdateState_FullMethodName           = "/game.GameService/UpdateState"
	GameService_UpdateStateFromEngine_FullMethodName = "/game.GameService/UpdateStateFromEngine"
	GameService_GetGameState_FullMethodName          = "/game.GameService/GetGameState"
	GameService_StreamGameState_FullMethodName       = "/game.GameService/StreamGameState"
	GameService_AddBullet_FullMethodName             = "/game.GameService/AddBullet"
	GameService_RemoveBullet_FullMethodName          = "/game.GameService/RemoveBullet"
	GameService_SetMap_FullMethodName                = "/game.GameService/SetMap"
	GameService_GetMap_FullMethodName                = "/game.GameService/GetMap"
	GameService_AddPlayer_FullMethodName             = "/game.GameService/AddPlayer"
	GameService_GetPlayerList_FullMethodName         = "/game.GameService/GetPlayerList"
	GameService_StartGame_FullMethodName             = "/game.GameService/StartGame"
)

// GameServiceClient is the client API for GameService service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type GameServiceClient interface {
	// Actualiza el estado del jugador y envia una actualizacion
	UpdateState(ctx context.Context, in *PlayerState, opts ...grpc.CallOption) (*GameState, error)
	// Actualiza el estado del jugador desde el engine
	UpdateStateFromEngine(ctx context.Context, in *PlayerState, opts ...grpc.CallOption) (*GameState, error)
	// Obtener estado del juego
	GetGameState(ctx context.Context, in *Empty, opts ...grpc.CallOption) (*GameState, error)
	// Devuelve actualizaciones en tiempo real
	StreamGameState(ctx context.Context, in *Empty, opts ...grpc.CallOption) (grpc.ServerStreamingClient[GameState], error)
	// Agregar una bala al servidor
	AddBullet(ctx context.Context, in *BulletState, opts ...grpc.CallOption) (*Empty, error)
	// Eliminar una bala del servidor
	RemoveBullet(ctx context.Context, in *BulletRemoveRequest, opts ...grpc.CallOption) (*Empty, error)
	// Establecer el mapa que se va a usar
	SetMap(ctx context.Context, in *MapRequest, opts ...grpc.CallOption) (*Empty, error)
	// Obtener el mapa actual
	GetMap(ctx context.Context, in *Empty, opts ...grpc.CallOption) (*MapResponse, error)
	// Añadir un método para agregar nuevos jugadores
	AddPlayer(ctx context.Context, in *PlayerRequest, opts ...grpc.CallOption) (*PlayerResponse, error)
	// Obtener el listado de jugadores
	GetPlayerList(ctx context.Context, in *Empty, opts ...grpc.CallOption) (*PlayerList, error)
	// Iniciar el juego (nuevo método)
	StartGame(ctx context.Context, in *Empty, opts ...grpc.CallOption) (*Empty, error)
}

type gameServiceClient struct {
	cc grpc.ClientConnInterface
}

func NewGameServiceClient(cc grpc.ClientConnInterface) GameServiceClient {
	return &gameServiceClient{cc}
}

func (c *gameServiceClient) UpdateState(ctx context.Context, in *PlayerState, opts ...grpc.CallOption) (*GameState, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(GameState)
	err := c.cc.Invoke(ctx, GameService_UpdateState_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *gameServiceClient) UpdateStateFromEngine(ctx context.Context, in *PlayerState, opts ...grpc.CallOption) (*GameState, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(GameState)
	err := c.cc.Invoke(ctx, GameService_UpdateStateFromEngine_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *gameServiceClient) GetGameState(ctx context.Context, in *Empty, opts ...grpc.CallOption) (*GameState, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(GameState)
	err := c.cc.Invoke(ctx, GameService_GetGameState_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *gameServiceClient) StreamGameState(ctx context.Context, in *Empty, opts ...grpc.CallOption) (grpc.ServerStreamingClient[GameState], error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	stream, err := c.cc.NewStream(ctx, &GameService_ServiceDesc.Streams[0], GameService_StreamGameState_FullMethodName, cOpts...)
	if err != nil {
		return nil, err
	}
	x := &grpc.GenericClientStream[Empty, GameState]{ClientStream: stream}
	if err := x.ClientStream.SendMsg(in); err != nil {
		return nil, err
	}
	if err := x.ClientStream.CloseSend(); err != nil {
		return nil, err
	}
	return x, nil
}

// This type alias is provided for backwards compatibility with existing code that references the prior non-generic stream type by name.
type GameService_StreamGameStateClient = grpc.ServerStreamingClient[GameState]

func (c *gameServiceClient) AddBullet(ctx context.Context, in *BulletState, opts ...grpc.CallOption) (*Empty, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(Empty)
	err := c.cc.Invoke(ctx, GameService_AddBullet_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *gameServiceClient) RemoveBullet(ctx context.Context, in *BulletRemoveRequest, opts ...grpc.CallOption) (*Empty, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(Empty)
	err := c.cc.Invoke(ctx, GameService_RemoveBullet_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *gameServiceClient) SetMap(ctx context.Context, in *MapRequest, opts ...grpc.CallOption) (*Empty, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(Empty)
	err := c.cc.Invoke(ctx, GameService_SetMap_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *gameServiceClient) GetMap(ctx context.Context, in *Empty, opts ...grpc.CallOption) (*MapResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(MapResponse)
	err := c.cc.Invoke(ctx, GameService_GetMap_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *gameServiceClient) AddPlayer(ctx context.Context, in *PlayerRequest, opts ...grpc.CallOption) (*PlayerResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(PlayerResponse)
	err := c.cc.Invoke(ctx, GameService_AddPlayer_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *gameServiceClient) GetPlayerList(ctx context.Context, in *Empty, opts ...grpc.CallOption) (*PlayerList, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(PlayerList)
	err := c.cc.Invoke(ctx, GameService_GetPlayerList_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *gameServiceClient) StartGame(ctx context.Context, in *Empty, opts ...grpc.CallOption) (*Empty, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(Empty)
	err := c.cc.Invoke(ctx, GameService_StartGame_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// GameServiceServer is the server API for GameService service.
// All implementations must embed UnimplementedGameServiceServer
// for forward compatibility.
type GameServiceServer interface {
	// Actualiza el estado del jugador y envia una actualizacion
	UpdateState(context.Context, *PlayerState) (*GameState, error)
	// Actualiza el estado del jugador desde el engine
	UpdateStateFromEngine(context.Context, *PlayerState) (*GameState, error)
	// Obtener estado del juego
	GetGameState(context.Context, *Empty) (*GameState, error)
	// Devuelve actualizaciones en tiempo real
	StreamGameState(*Empty, grpc.ServerStreamingServer[GameState]) error
	// Agregar una bala al servidor
	AddBullet(context.Context, *BulletState) (*Empty, error)
	// Eliminar una bala del servidor
	RemoveBullet(context.Context, *BulletRemoveRequest) (*Empty, error)
	// Establecer el mapa que se va a usar
	SetMap(context.Context, *MapRequest) (*Empty, error)
	// Obtener el mapa actual
	GetMap(context.Context, *Empty) (*MapResponse, error)
	// Añadir un método para agregar nuevos jugadores
	AddPlayer(context.Context, *PlayerRequest) (*PlayerResponse, error)
	// Obtener el listado de jugadores
	GetPlayerList(context.Context, *Empty) (*PlayerList, error)
	// Iniciar el juego (nuevo método)
	StartGame(context.Context, *Empty) (*Empty, error)
	mustEmbedUnimplementedGameServiceServer()
}

// UnimplementedGameServiceServer must be embedded to have
// forward compatible implementations.
//
// NOTE: this should be embedded by value instead of pointer to avoid a nil
// pointer dereference when methods are called.
type UnimplementedGameServiceServer struct{}

func (UnimplementedGameServiceServer) UpdateState(context.Context, *PlayerState) (*GameState, error) {
	return nil, status.Errorf(codes.Unimplemented, "method UpdateState not implemented")
}
func (UnimplementedGameServiceServer) UpdateStateFromEngine(context.Context, *PlayerState) (*GameState, error) {
	return nil, status.Errorf(codes.Unimplemented, "method UpdateStateFromEngine not implemented")
}
func (UnimplementedGameServiceServer) GetGameState(context.Context, *Empty) (*GameState, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetGameState not implemented")
}
func (UnimplementedGameServiceServer) StreamGameState(*Empty, grpc.ServerStreamingServer[GameState]) error {
	return status.Errorf(codes.Unimplemented, "method StreamGameState not implemented")
}
func (UnimplementedGameServiceServer) AddBullet(context.Context, *BulletState) (*Empty, error) {
	return nil, status.Errorf(codes.Unimplemented, "method AddBullet not implemented")
}
func (UnimplementedGameServiceServer) RemoveBullet(context.Context, *BulletRemoveRequest) (*Empty, error) {
	return nil, status.Errorf(codes.Unimplemented, "method RemoveBullet not implemented")
}
func (UnimplementedGameServiceServer) SetMap(context.Context, *MapRequest) (*Empty, error) {
	return nil, status.Errorf(codes.Unimplemented, "method SetMap not implemented")
}
func (UnimplementedGameServiceServer) GetMap(context.Context, *Empty) (*MapResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetMap not implemented")
}
func (UnimplementedGameServiceServer) AddPlayer(context.Context, *PlayerRequest) (*PlayerResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method AddPlayer not implemented")
}
func (UnimplementedGameServiceServer) GetPlayerList(context.Context, *Empty) (*PlayerList, error) {
	return nil, status.Errorf(codes.Unimplemented, "method GetPlayerList not implemented")
}
func (UnimplementedGameServiceServer) StartGame(context.Context, *Empty) (*Empty, error) {
	return nil, status.Errorf(codes.Unimplemented, "method StartGame not implemented")
}
func (UnimplementedGameServiceServer) mustEmbedUnimplementedGameServiceServer() {}
func (UnimplementedGameServiceServer) testEmbeddedByValue()                     {}

// UnsafeGameServiceServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to GameServiceServer will
// result in compilation errors.
type UnsafeGameServiceServer interface {
	mustEmbedUnimplementedGameServiceServer()
}

func RegisterGameServiceServer(s grpc.ServiceRegistrar, srv GameServiceServer) {
	// If the following call pancis, it indicates UnimplementedGameServiceServer was
	// embedded by pointer and is nil.  This will cause panics if an
	// unimplemented method is ever invoked, so we test this at initialization
	// time to prevent it from happening at runtime later due to I/O.
	if t, ok := srv.(interface{ testEmbeddedByValue() }); ok {
		t.testEmbeddedByValue()
	}
	s.RegisterService(&GameService_ServiceDesc, srv)
}

func _GameService_UpdateState_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(PlayerState)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(GameServiceServer).UpdateState(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: GameService_UpdateState_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(GameServiceServer).UpdateState(ctx, req.(*PlayerState))
	}
	return interceptor(ctx, in, info, handler)
}

func _GameService_UpdateStateFromEngine_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(PlayerState)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(GameServiceServer).UpdateStateFromEngine(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: GameService_UpdateStateFromEngine_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(GameServiceServer).UpdateStateFromEngine(ctx, req.(*PlayerState))
	}
	return interceptor(ctx, in, info, handler)
}

func _GameService_GetGameState_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(Empty)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(GameServiceServer).GetGameState(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: GameService_GetGameState_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(GameServiceServer).GetGameState(ctx, req.(*Empty))
	}
	return interceptor(ctx, in, info, handler)
}

func _GameService_StreamGameState_Handler(srv interface{}, stream grpc.ServerStream) error {
	m := new(Empty)
	if err := stream.RecvMsg(m); err != nil {
		return err
	}
	return srv.(GameServiceServer).StreamGameState(m, &grpc.GenericServerStream[Empty, GameState]{ServerStream: stream})
}

// This type alias is provided for backwards compatibility with existing code that references the prior non-generic stream type by name.
type GameService_StreamGameStateServer = grpc.ServerStreamingServer[GameState]

func _GameService_AddBullet_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(BulletState)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(GameServiceServer).AddBullet(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: GameService_AddBullet_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(GameServiceServer).AddBullet(ctx, req.(*BulletState))
	}
	return interceptor(ctx, in, info, handler)
}

func _GameService_RemoveBullet_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(BulletRemoveRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(GameServiceServer).RemoveBullet(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: GameService_RemoveBullet_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(GameServiceServer).RemoveBullet(ctx, req.(*BulletRemoveRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _GameService_SetMap_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(MapRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(GameServiceServer).SetMap(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: GameService_SetMap_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(GameServiceServer).SetMap(ctx, req.(*MapRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _GameService_GetMap_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(Empty)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(GameServiceServer).GetMap(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: GameService_GetMap_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(GameServiceServer).GetMap(ctx, req.(*Empty))
	}
	return interceptor(ctx, in, info, handler)
}

func _GameService_AddPlayer_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(PlayerRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(GameServiceServer).AddPlayer(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: GameService_AddPlayer_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(GameServiceServer).AddPlayer(ctx, req.(*PlayerRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _GameService_GetPlayerList_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(Empty)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(GameServiceServer).GetPlayerList(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: GameService_GetPlayerList_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(GameServiceServer).GetPlayerList(ctx, req.(*Empty))
	}
	return interceptor(ctx, in, info, handler)
}

func _GameService_StartGame_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(Empty)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(GameServiceServer).StartGame(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: GameService_StartGame_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(GameServiceServer).StartGame(ctx, req.(*Empty))
	}
	return interceptor(ctx, in, info, handler)
}

// GameService_ServiceDesc is the grpc.ServiceDesc for GameService service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var GameService_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "game.GameService",
	HandlerType: (*GameServiceServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "UpdateState",
			Handler:    _GameService_UpdateState_Handler,
		},
		{
			MethodName: "UpdateStateFromEngine",
			Handler:    _GameService_UpdateStateFromEngine_Handler,
		},
		{
			MethodName: "GetGameState",
			Handler:    _GameService_GetGameState_Handler,
		},
		{
			MethodName: "AddBullet",
			Handler:    _GameService_AddBullet_Handler,
		},
		{
			MethodName: "RemoveBullet",
			Handler:    _GameService_RemoveBullet_Handler,
		},
		{
			MethodName: "SetMap",
			Handler:    _GameService_SetMap_Handler,
		},
		{
			MethodName: "GetMap",
			Handler:    _GameService_GetMap_Handler,
		},
		{
			MethodName: "AddPlayer",
			Handler:    _GameService_AddPlayer_Handler,
		},
		{
			MethodName: "GetPlayerList",
			Handler:    _GameService_GetPlayerList_Handler,
		},
		{
			MethodName: "StartGame",
			Handler:    _GameService_StartGame_Handler,
		},
	},
	Streams: []grpc.StreamDesc{
		{
			StreamName:    "StreamGameState",
			Handler:       _GameService_StreamGameState_Handler,
			ServerStreams: true,
		},
	},
	Metadata: "game.proto",
}
