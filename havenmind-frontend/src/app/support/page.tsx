'use client'
import { useState } from 'react'
import Navbar from '@/components/Navbar'

export default function Support() {
  const [message, setMessage] = useState('')
  const [messages] = useState([
    { id: 1, text: 'Hi, I\'m feeling overwhelmed with assignments', sender: 'you', time: '2:30 PM' },
    { id: 2, text: 'I understand that feeling. What\'s been the most challenging part?', sender: 'peer', time: '2:32 PM' },
    { id: 3, text: 'Just the workload and deadlines piling up', sender: 'you', time: '2:33 PM' }
  ])

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Peer Support Network</h1>
        
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold mb-4">Available Peers</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg cursor-pointer">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Anonymous Peer #1</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg cursor-pointer">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Anonymous Peer #2</span>
              </div>
            </div>
            <button className="w-full mt-4 bg-red-600 text-white py-2 rounded-lg hover:bg-red-700">
              🚨 Crisis Support
            </button>
          </div>

          <div className="md:col-span-2 bg-white rounded-lg shadow">
            <div className="p-4 border-b">
              <h3 className="font-semibold">Chat with Anonymous Peer #1</h3>
            </div>
            
            <div className="h-96 p-4 overflow-y-auto">
              {messages.map(msg => (
                <div key={msg.id} className={`mb-4 ${msg.sender === 'you' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block p-3 rounded-lg max-w-xs ${
                    msg.sender === 'you' ? 'bg-indigo-600 text-white' : 'bg-gray-200'
                  }`}>
                    {msg.text}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">{msg.time}</div>
                </div>
              ))}
            </div>
            
            <div className="p-4 border-t">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Type your message..."
                  className="flex-1 p-3 border rounded-lg"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                />
                <button className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700">
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}