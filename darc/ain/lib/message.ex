defmodule Message do
  defstruct [:uid, :sender_pid, :receiver_pid, :sender_uid, :receiver_uid, :content, :parameters, :timestamp]

  @doc """
  创建消息函数

  ## 参数
    - sender: 发送者
    - receiver: 接收者
    - content: 内容
    - parameters: 参数 (map)
  """
  def create(sender_pid \\ nil, receiver_pid \\ nil, sender_uid \\ "", receiver_uid \\ "", content, parameters) do
    %Message{
      uid: UUID.uuid4(),
      sender_pid: sender_pid,
      receiver_pid: receiver_pid,
      sender_uid: sender_uid,
      receiver_uid: receiver_uid,
      content: content,
      parameters: parameters,
      timestamp: DateTime.utc_now() |> DateTime.to_iso8601()
    }
  end

  def parse(%Message{} = message) do
    %{
      uid: message.uid,
      sender_pid: message.sender_pid,
      receiver_pid: message.receiver_pid,
      sender_uid: message.sender_uid,
      receiver_uid: message.receiver_uid,
      content: message.content,
      parameters: message.parameters,
      timestamp: message.timestamp,
    }
  end
end
