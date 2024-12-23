import { useState } from 'react'
import { Button } from './ui/button'

const BASE_URL = "https://wildcard-voker.onrender.com"

interface API {
  id: string
  name: string
  description: string
  icon: string
  scopes: string[]
  flow: Record<string, any>
}

const gmailScopes = "https://www.googleapis.com/auth/gmail.addons.current.action.compose https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.settings.basic https://www.googleapis.com/auth/gmail.addons.current.message.metadata https://www.googleapis.com/auth/gmail.settings.sharing https://www.googleapis.com/auth/gmail.insert https://mail.google.com/ https://www.googleapis.com/auth/gmail.addons.current.message.readonly https://www.googleapis.com/auth/gmail.labels https://www.googleapis.com/auth/gmail.addons.current.message.action https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.metadata".split(" ")

const apis: API[] = [
  {
    id: 'gmail',
    name: 'Gmail',
    description: 'Connect to your Gmail account to send and receive emails',
    icon: '📧',
    scopes: gmailScopes,
    flow: {
      authorizationCode: {
        authorizationUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
        tokenUrl: 'https://oauth2.googleapis.com/token',
        refreshUrl: 'https://oauth2.googleapis.com/token',
        scopes: gmailScopes.map(scope => ({scope, value: scope}))
      }
    }
  },
]

export function AuthPortal() {
  const [loading, setLoading] = useState<string | null>(null)

  const handleConnect = async (api: API) => {
    console.log(`Connecting to API: ${api.id}`)
    try {
      setLoading(api.id)
      const response = await fetch(BASE_URL + '/auth/oauth_flow/' + api.id, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_service: api.id,
          webhook_url: BASE_URL + '/auth_webhook',
          required_scopes: api.scopes,
          flow: api.flow
        }),
      })

      const data = await response.json()
      if (data.authorization_url) {
        window.location.href = data.authorization_url
      }
    } catch (error) {
      console.error('Error starting OAuth flow:', error)
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Connect Your APIs
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            Select an API to connect and authorize access
          </p>
        </div>

        <div className="space-y-4">
          {apis.map((api) => (
            <div
              key={api.id}
              className="bg-white shadow rounded-lg p-6 flex items-center justify-between"
            >
              <div className="flex items-center space-x-4">
                <div className="text-4xl">{api.icon}</div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    {api.name}
                  </h2>
                  <p className="text-gray-500">{api.description}</p>
                </div>
              </div>
              <Button
                onClick={() => handleConnect(api)}
                disabled={loading === api.id}
              >
                {loading === api.id ? 'Connecting...' : 'Connect'}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
