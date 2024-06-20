defmodule Ain.ActorModelLauncher do
  alias Ain.ActorModelServer

  # 接收 JSON 数据字符串
  def launch(json_data) do
    case Jason.decode(json_data) do
      {:ok, data} ->
        # 检查数据格式是否符合预期
        case validate_data(data) do
          :ok ->
            {:ok, pid} = ActorModelServer.start_link(data)
            # 调用 GenServer 函数打印日志
            ActorModelServer.print_logs(pid)

          {:error, error_msg} ->
            # 数据格式错误，抛出异常
            raise ArgumentError, message: error_msg
        end

      {:error, reason} ->
        # JSON 解析失败，打印错误信息
        IO.puts("Failed to decode JSON: #{reason}")
    end
  end

  # 验证数据是否符合预期格式
  defp validate_data(%{"init" => _init, "env" => _env, "logs" => _logs}) do
    :ok
  end
  defp validate_data(_), do: {:error, "Invalid data format"}
end
