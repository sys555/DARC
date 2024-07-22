defmodule MessageTest do
  use ExUnit.Case
  alias Message

  @valid_sender "sender1"
  @valid_receiver "receiver1"
  @valid_role "fetch_data"
  @valid_parameters %{
    data_id: "12345",
    additional_info: "Some information"
  }

  describe "create/4" do
    test "creates a message with the correct structure" do
      message = Message.create(@valid_sender, @valid_receiver, @valid_role, @valid_parameters)

      assert %Message{} = message
      assert message.sender == @valid_sender
      assert message.receiver == @valid_receiver
      assert message.content.role == @valid_role
      assert message.content.parameters == @valid_parameters
      assert is_binary(message.uuid)
      assert message.timestamp =~ ~r/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3,6}Z/
    end

    test "generates a unique UUID for each message" do
      message1 = Message.create(@valid_sender, @valid_receiver, @valid_role, @valid_parameters)
      message2 = Message.create(@valid_sender, @valid_receiver, @valid_role, @valid_parameters)

      assert message1.uuid != message2.uuid
    end

    test "generates a valid ISO8601 timestamp" do
      message = Message.create(@valid_sender, @valid_receiver, @valid_role, @valid_parameters)

      assert match?({:ok, _, _}, DateTime.from_iso8601(message.timestamp))
    end
  end

  describe "parse/1" do
    test "parses a message correctly" do
      message = Message.create(@valid_sender, @valid_receiver, @valid_role, @valid_parameters)
      parsed_message = Message.parse(message)

      assert parsed_message.uuid == message.uuid
      assert parsed_message.sender == message.sender
      assert parsed_message.receiver == message.receiver
      assert parsed_message.role == message.content.role
      assert parsed_message.parameters == message.content.parameters
      assert parsed_message.timestamp == message.timestamp
    end
  end
end
