defmodule Ain.Python do
  @doc """
  Start python instance with specified path
  """
  # def start(custom_path \\ nil) do
  #   path = case custom_path do
  #     nil ->
  #       #BUG: :ain path error
  #       [:code.priv_dir(:ain), "python"] |> Path.join()
  #     _ ->
  #       [:code.priv_dir(:ain), custom_path] |> Path.join()
  #   end

  #   {:ok, pid} = :python.start([
  #     {:python_path, to_charlist(path)}
  #   ])
  #   pid
  # end

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
