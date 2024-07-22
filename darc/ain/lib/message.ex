defmodule Message do
  defstruct [:uuid, :sender, :receiver, :content, :timestamp]

  @doc """
  创建消息函数

  ## 参数
    - sender: 发送者
    - receiver: 接收者
    - role: 角色
    - parameters: 参数 (map)
  """
  def create(sender, receiver, role, parameters) do
    %Message{
      uuid: UUID.uuid4(),
      sender: sender,
      receiver: receiver,
      content: %{
        role: role,
        parameters: parameters,
      },
      timestamp: DateTime.utc_now() |> DateTime.to_iso8601()
    }
  end

  def parse(%Message{} = message) do
    %{
      uuid: message.uuid,
      sender: message.sender,
      receiver: message.receiver,
      role: message.content.role,
      parameters: message.content.parameters,
      timestamp: message.timestamp
    }
  end
end
