defmodule Ain.Python do
  def start(env) do
    case :code.priv_dir(:ain) do
      {:error, :bad_name} ->
        {:error, :bad_name}

      priv_dir_path ->
        path = Path.join([priv_dir_path, env])

        {:ok, pid} = :python.start([
          {:python_path, to_charlist(path)}
        ])
        pid
    end
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
