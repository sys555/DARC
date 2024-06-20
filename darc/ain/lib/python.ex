defmodule Ain.Python do
  @doc """
  Start python instance with specified path
  """
  def start(custom_path \\ nil) do
    path = case custom_path do
      nil ->
        #BUG: :ain path error
        [:code.priv_dir(:ain), "python"] |> Path.join()
      _ ->
        custom_path
    end

    {:ok, pid} = :python.start([
      {:python_path, to_charlist(path)}
    ])
    pid
  end

  def call(pid, m, f, a \\ []) do
    :python.call(pid, m, f, a)
  end

  def cast(pid, message) do
    :python.cast(pid, message)
  end

  def stop(pid) do
    :python.stop(pid)
  end
end
