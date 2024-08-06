# defmodule Mix.Tasks.Invoke do
#   use Mix.Task

#   @shortdoc "Invoke functions in ain"

#   def run(args) do
#     # 启动所有必要的应用
#     {:ok, _} = Application.ensure_all_started(:ain)
#     IO.inspect("======================================================================")
#     IO.inspect(args)
#     IO.inspect("======================================================================")
#     # 继续处理原有的逻辑
#     case args do
#       ["start", str] -> start_function(str)
#       # ["send", uuid, message] -> send_function(uuid, message)
#       ["load", graph_id] -> load_function(graph_id)
#       # ["test", arg1] -> test_function(arg1)
#       _ -> Mix.raise("Unknown command")
#     end
#   end

#   defp start_function(str) do
#     uuid = MyModule.start(str)
#     IO.puts("UUID: #{uuid}")
#   end

#   defp send_function(uuid, message) do
#     message_map = Jason.decode!(message)
#     Ain.Bridge.send(uuid, message_map)
#   end

#   defp load_function(graph_id) do
#     Ain.Bridge.load(graph_id)
#   end

#   defp test_function(arg1) do
#     # IO.inspect(arg1, arg2)
#   end
# end

defmodule Mix.Tasks.Invoke do
  use Mix.Task

  @shortdoc "Invoke functions in ain"

  def run(args) do
    # 启动所有必要的应用
    {:ok, _} = Application.ensure_all_started(:ain)
    # 继续处理原有的逻辑
    case args do
      ["test", arg1, arg2] -> test_function(arg1, arg2)
      _ -> Mix.raise("Unknown command")
    end
  end

  defp test_function(arg1, arg2) do
    IO.puts("Result from Elixir: #{arg1} and #{arg2}")
  end
end
