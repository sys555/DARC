defmodule Mix.Tasks.Invoke do
  use Mix.Task

  @shortdoc "Invoke functions in MyModule"

  def run(["start", str]) do
    uuid = MyModule.start(str)
    IO.puts("UUID: #{uuid}")
  end

  def run(["send", uuid, message]) do
    # 将 JSON 字符串转换为 Elixir map
    message_map = Jason.decode!(message)
    MyModule.send(uuid, message_map)
  end
end
