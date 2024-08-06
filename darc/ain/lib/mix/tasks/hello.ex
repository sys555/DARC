defmodule Mix.Tasks.Hello do
  use Mix.Task

  @shortdoc "Prints Hello, World!"
  def run(_) do
    IO.puts("Hello, World!")
  end
end
