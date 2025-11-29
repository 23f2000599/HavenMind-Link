import Navbar from '@/components/Navbar'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            HavenMind Link
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            AI Sentinel for Student Wellbeing and Institutional Accountability
          </p>
          <div className="grid md:grid-cols-3 gap-6 mt-12">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="font-semibold mb-2">AI Monitoring</h3>
              <p className="text-gray-600">Cognitive load tracking and burnout prevention</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="font-semibold mb-2">Peer Support</h3>
              <p className="text-gray-600">Anonymous student-to-student connections</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="font-semibold mb-2">Crisis Response</h3>
              <p className="text-gray-600">Secure escalation and accountability system</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
