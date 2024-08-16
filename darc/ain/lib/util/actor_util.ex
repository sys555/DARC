defmodule Util.ActorUtil do
  alias DB.Repo
  alias DB.Factory
  alias DB.{Actor, Edge, Task}
  alias Util.DBUtil

  def connect_actors(edges, actor_specs) do
    Enum.each(edges, fn %DB.Edge{from_uid: from_uid, to_uid: to_uid} ->
      from_pid = :global.whereis_name(from_uid)
      to_pid = :global.whereis_name(to_uid)

      cond do
        from_pid == :undefined ->
          IO.puts("Failed to find PID for from_uid: #{from_uid}")

        to_pid == :undefined ->
          IO.puts("Failed to find PID for to_uid: #{to_uid}")

        true ->
          case get_role_by_uid(to_uid, actor_specs) do
            {:ok, to_role} ->
              message = %Message{
                content: "original message",
                parameters: %{
                  "to_uid" => to_uid,
                  "to_pid" => to_pid,
                  "to_role" => to_role
                }
              }

              GenServer.cast(from_pid, {:explore, message})

            {:error, reason} ->
              IO.puts("Failed to get role for to_uid: #{to_uid}. Reason: #{reason}")
          end
      end
    end)
  end

  defp get_role_by_uid(uid, actor_specs) do
    case Enum.find(actor_specs, fn %{uid: actor_uid} -> actor_uid == uid end) do
      nil -> {:error, "Role not found"}
      %{role: role} -> {:ok, role}
    end
  end

  defp get_role(uid, actor_specs) do
    actor_specs
    |> Enum.find(fn actor_spec -> actor_spec.uid == uid end)
    |> Map.get(:role)
  end

  def get_uid_by_pid(address_book, target_pid) do
    address_book
    |> Enum.find(fn {_uid, pid} -> pid == target_pid end)
    |> case do
      {uid, _pid} -> uid
      nil -> nil
    end
  end
end
