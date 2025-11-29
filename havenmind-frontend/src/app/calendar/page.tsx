'use client'
import { useState } from 'react'
import Navbar from '@/components/Navbar'

export default function Calendar() {
  const [newEvent, setNewEvent] = useState('')
  const [events] = useState([
    { id: 1, title: 'Math Assignment Due', date: '2024-11-15', stress: 'high' },
    { id: 2, title: 'Wellness Break', date: '2024-11-16', stress: 'low' },
    { id: 3, title: 'Project Presentation', date: '2024-11-18', stress: 'high' }
  ])

  const getStressColor = (stress: string) => {
    switch(stress) {
      case 'high': return 'bg-red-100 border-red-300'
      case 'medium': return 'bg-yellow-100 border-yellow-300'
      case 'low': return 'bg-green-100 border-green-300'
      default: return 'bg-gray-100 border-gray-300'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Emotion-Aware Calendar</h1>
        
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h3 className="font-semibold mb-4">Add New Event</h3>
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="Describe your deadline or event..."
              className="flex-1 p-3 border rounded-lg"
              value={newEvent}
              onChange={(e) => setNewEvent(e.target.value)}
            />
            <button className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700">
              Add Event
            </button>
          </div>
        </div>

        <div className="grid gap-4">
          <h3 className="font-semibold text-lg">Upcoming Events</h3>
          {events.map(event => (
            <div key={event.id} className={`p-4 rounded-lg border-2 ${getStressColor(event.stress)}`}>
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-medium">{event.title}</h4>
                  <p className="text-sm text-gray-600">{event.date}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  event.stress === 'high' ? 'bg-red-200 text-red-800' :
                  event.stress === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                  'bg-green-200 text-green-800'
                }`}>
                  {event.stress} stress
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}