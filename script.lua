local function notif(text)
	game.StarterGui:SetCore("SendNotification", {
		Title = "Netsploit 📡",
		Text = text,
		Image = "rbxassetid://75409762642443",
		Button1 = "Dismiss"
	})
end

local ws = ws or wst or WebSocket or websocket or Websocket or (function() notif("🔴 Executor unsupported, missing Websockets support.") error("📡 Netsploit has errored:\n `-> Unsupported executor") end)()
local sock
local success, err = pcall(function() sock = ws.connect("ws://".._G.IP..":1337"))

if success then
	notif("🟢 Connection established")
else
	notif("🔴 Connection failed, see console")
	error("📡 Netsploit has errored:\n `-> "..err)
end

sock.OnMessage:Connect(function(message)
	notif("🔵 Received a script")
	sock:Send("[success]")

	local t = task.spawn(function() loadstring(message)() end)
end)