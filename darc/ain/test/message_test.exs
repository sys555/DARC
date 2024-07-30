defmodule MessageTest do
  use ExUnit.Case
  alias Message

  test "create/4 correctly creates a Message struct" do
    sender = "Alice"
    receiver = "Bob"
    content = "Hello, Bob!"
    parameters = %{"key" => "value"}

    message = Message.create(sender, receiver, content, parameters)

    assert %Message{
            uuid: _,
            sender: ^sender,
            receiver: ^receiver,
            content: ^content,
            parameters: ^parameters,
            timestamp: _
          } = message

    assert String.length(message.uuid) > 0
    assert DateTime.from_iso8601(message.timestamp) |> elem(0) == :ok
  end

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
