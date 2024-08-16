defmodule Masrpc.LoadRequest do
  @moduledoc false

  use Protobuf, syntax: :proto3, protoc_gen_elixir_version: "0.12.0"

  field :graph_id, 1, type: :string, json_name: "graphId"
end

defmodule Masrpc.SendRequest.MessageEntry do
  @moduledoc false

  use Protobuf, map: true, syntax: :proto3, protoc_gen_elixir_version: "0.12.0"

  field :key, 1, type: :string
  field :value, 2, type: :string
end

defmodule Masrpc.SendRequest do
  @moduledoc false

  use Protobuf, syntax: :proto3, protoc_gen_elixir_version: "0.12.0"

  field :uid, 1, type: :string
  field :message, 2, repeated: true, type: Masrpc.SendRequest.MessageEntry, map: true
end

defmodule Masrpc.GetLogRequest do
  @moduledoc false

  use Protobuf, syntax: :proto3, protoc_gen_elixir_version: "0.12.0"

  field :uid, 1, type: :string
end

defmodule Masrpc.OperationResponse do
  @moduledoc false

  use Protobuf, syntax: :proto3, protoc_gen_elixir_version: "0.12.0"

  field :status, 1, type: :string
  field :logs, 2, repeated: true, type: :string
end

defmodule Masrpc.MasRPC.Service do
  @moduledoc false

  use GRPC.Service, name: "masrpc.MasRPC", protoc_gen_elixir_version: "0.12.0"

  rpc :Load, Masrpc.LoadRequest, Masrpc.OperationResponse

  rpc :Send, Masrpc.SendRequest, Masrpc.OperationResponse

  rpc :GetLog, Masrpc.GetLogRequest, Masrpc.OperationResponse
end

defmodule Masrpc.MasRPC.Stub do
  @moduledoc false

  use GRPC.Stub, service: Masrpc.MasRPC.Service
end