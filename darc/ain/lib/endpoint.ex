defmodule Masrpc.Endpoint do
  use GRPC.Endpoint

  intercept GRPC.Server.Interceptors.Logger
  run Masrpc.Server
end
