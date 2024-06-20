defmodule AinTest do
  use ExUnit.Case
  doctest Ain

  test "greets the world" do
    assert Ain.hello() == :world
  end
end
