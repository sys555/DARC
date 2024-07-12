defmodule DB.Task do
  use Ecto.Schema
  import Ecto.Changeset

  @primary_key {:uid, :binary_id, autogenerate: true}
  schema "tasks" do
    field :ttl, :integer
    field :nodes, :map
    field :input, :map
    field :output, :map
    field :diff_graph, :map
    field :whole_graph, :map
    field :logs, :map

    timestamps()
  end

  @doc """
  创建或更新 Task 的 changeset。
  """
  def changeset(task, attrs) do
    task
    |> cast(attrs, [:ttl, :nodes, :input, :output, :diff_graph, :whole_graph, :logs])
    |> validate_required([:ttl, :nodes, :input, :output, :diff_graph, :whole_graph, :logs])
  end

end
