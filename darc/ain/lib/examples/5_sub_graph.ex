defmodule SubGraphExample do
  {:ok, contract_pid} = GraphContract.start_link([])
end
