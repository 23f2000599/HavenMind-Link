export default function Navbar() {
  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="font-bold text-xl text-indigo-600">HavenMind Link</div>
          <div className="flex space-x-6">
            <a href="/dashboard" className="text-gray-600 hover:text-indigo-600">Dashboard</a>
            <a href="/calendar" className="text-gray-600 hover:text-indigo-600">Calendar</a>
            <a href="/support" className="text-gray-600 hover:text-indigo-600">Support</a>
            <a href="/journal" className="text-gray-600 hover:text-indigo-600">Journal</a>
          </div>
        </div>
      </div>
    </nav>
  )
}