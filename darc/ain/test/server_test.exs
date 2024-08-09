defmodule Mas.ServerTest do
  use ExUnit.Case
  alias Mas.Server
  alias Mas.{LoadRequest, SendRequest, GetLogRequest, OperationResponse}

  setup do
    # Optionally start any necessary processes or mocks here
    :ok
  end

  test "load function" do
    request = %LoadRequest{graph_id: "test_graph"}
    response = Server.load(request, nil)
    assert %OperationResponse{status: "Load complete"} = response
  end

  test "send function" do
    request = %SendRequest{uid: "test_uid", message: "test"}
    response = Server.send(request, nil)
    assert %OperationResponse{status: "Send completed"} = response
  end

  test "get_log function" do
    request = %GetLogRequest{uid: "test_uid"}
    response = Server.get_log(request, nil)
    assert %OperationResponse{status: "Get log complete", logs: [%{}, %{}]} = response
  end
end
