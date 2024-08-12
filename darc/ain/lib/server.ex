defmodule Masrpc.Server do
  use GRPC.Server, service: Masrpc.MasRPC.Service
  alias MAS

  @spec load(Masrpc.LoadRequest.t(), GRPC.Server.Stream.t()) :: Masrpc.OperationResponse.t()
  def load(%Masrpc.LoadRequest{graph_id: graph_id}, _stream) do
    mas_pid = MasrpcServerState.get_mas_pid()
    :ok = GenServer.cast(mas_pid, {:load, graph_id, self()})
    receive do
      {:load_complete, _graph_id} ->
        Masrpc.OperationResponse.new(status: "Load complete")
    after
      42_000 ->
        Masrpc.OperationResponse.new(status: "Load time out")
    end
  end

  @spec send(Masrpc.SendRequest.t(), GRPC.Server.Stream.t()) :: Masrpc.OperationResponse.t()
  def send(%Masrpc.SendRequest{uid: uid, message: message}, _stream) do
    mas_pid = MasrpcServerState.get_mas_pid()
    :ok = GenServer.call(mas_pid, {:send, uid, message})
    Masrpc.OperationResponse.new(status: "Send completed")
  end

  @spec get_log(Masrpc.GetLogRequest.t(), GRPC.Server.Stream.t()) :: Masrpc.OperationResponse.t()
  def get_log(%Masrpc.GetLogRequest{uid: uid}, _stream) do
    mas_pid = MasrpcServerState.get_mas_pid()
    :ok = GenServer.cast(mas_pid, {:get_log, uid, self()})
    receive do
      {:get_log_complete, logs} ->
        parsed_logs = Enum.map(logs, &Message.parse/1)
        # 使用 Enum.map 对每个元素进行编码
        json_list = Enum.map(parsed_logs, fn element ->
          element
          |> Map.update!(:receiver_pid, &inspect/1)
          |> Map.update!(:sender_pid, &inspect/1)
          |> Jason.encode!()
        end)
        # parsed_logs = Enum.map(parsed_logs, &inspect/1)
        Masrpc.OperationResponse.new(status: "Get log complete", logs: json_list)
    end
  end
end
