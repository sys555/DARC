defmodule Mix.Tasks.SendMessage do
  use Mix.Task

  @shortdoc "Sends a message with a UUID and a map"

  def run(args) do
    {opts, _, _} = OptionParser.parse(args, switches: [json: :string])

    case Keyword.fetch(opts, :json) do
      {:ok, json_str} ->
        case Jason.decode(json_str) do
          {:ok, %{"uuid" => uuid, "message" => message}} ->
            send_message(uuid, message)
          _ ->
            IO.puts("Invalid JSON format")
        end
      _ ->
        IO.puts("Usage: mix send_message --json '<json_data>'")
    end
  end

  defp send_message(uuid, message) do
    IO.puts("UUID: #{uuid}")
    IO.inspect(message, label: "Message")
  end
end
