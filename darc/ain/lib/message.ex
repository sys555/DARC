defmodule Message do
  defstruct [:uuid, :sender, :receiver, :content, :parameters, :timestamp]

  @doc """
  创建消息函数

  ## 参数
    - sender: 发送者
    - receiver: 接收者
    - content: 内容
    - parameters: 参数 (map)
  """
  def create(sender, receiver, content, parameters) do
    %Message{
      uuid: UUID.uuid4(),
      sender: sender,
      receiver: receiver,
      content: content,
      parameters: parameters,
      timestamp: DateTime.utc_now() |> DateTime.to_iso8601()
    }
  end

  def parse(%Message{} = message) do
    %{
      uuid: message.uuid,
      sender: message.sender,
      receiver: message.receiver,
      content: message.content,
      parameters: message.parameters,
      timestamp: message.timestamp,
    }
  end
end
