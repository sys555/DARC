defmodule MyModule do
  def start(str) do
    uuid = "123-01"
    IO.puts("Start function called with: #{str}")
    uuid
  end

  def send(uuid, message) do
    IO.puts("Send function called with: #{uuid} and message: #{inspect(message)}")
    :ok
  end
end
