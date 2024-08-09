defmodule MessageTest do
  use ExUnit.Case
  alias Message

  test "parse/1 correctly parses a Message struct to a map" do
    message = %Message{
      uuid: UUID.uuid4(),
      sender: "Alice",
      receiver: "Bob",
      content: "Hello, Bob!",
      parameters: %{"key" => "value"},
      timestamp: DateTime.utc_now() |> DateTime.to_iso8601()
    }

    parsed = Message.parse(message)

    assert parsed == %{
            uuid: message.uuid,
            sender: message.sender,
            receiver: message.receiver,
            content: message.content,
            parameters: message.parameters,
            timestamp: message.timestamp
          }
  end
end
