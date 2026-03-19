"use client"

import Chat from "../../src/components/chat"
import MenuPanel from "../../src/components/menuPanel"
import ProtectedRoute from "../../src/components/protectedroute"

export default function ChatPage(){

  return(
    <ProtectedRoute>
      <MenuPanel />
      <div className="p-6 max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-gray-800"></h1>
        <Chat />
      </div>
    </ProtectedRoute>
  )
}