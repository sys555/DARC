defmodule LoadOneNode do
  alias Ain.ActorModelLauncher

  def run do
    # 直接指定当前目录下的 JSON 文件路径
    json_path = Path.expand("./1_load_one_node.json", __DIR__)

    case File.read(json_path) do
      {:ok, json_data} ->
        # 文件读取成功，调用 ActorModelLauncher.launch
        ActorModelLauncher.launch(json_data)

      {:error, reason} ->
        # 文件读取失败，打印错误信息
        IO.puts("Failed to read JSON file: #{reason}")
    end
  end
end
