import os

def process_file(filepath, login_component_type):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add state variables
    content = content.replace('const [loading, setLoading] = useState(false);',
                              'const [loading, setLoading] = useState(false);\n  const [password, setPassword] = useState("password123");\n  const [loginError, setLoginError] = useState("");')

    # Remove useEffect auto-login and replace with handleLogin
    if login_component_type == "mp":
        old_login = """  // Login MP based on selected persona
  useEffect(() => {
    async function loginAndFetch() {
      setLoading(true);
      try {
        const authData = await api.login(selectedPersona, "password123");
        localStorage.setItem("token", authData.access_token);
        setUser(authData);
        
        // Fetch initially
        await fetchData();
      } catch (err) {
        console.error("Auto login failed:", err);
      } finally {
        setLoading(false);
      }
    }
    loginAndFetch();
  }, [selectedPersona]);"""
        
        new_login = """  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLoginError("");
    try {
      const authData = await api.login(selectedPersona, password);
      localStorage.setItem("token", authData.access_token);
      setUser(authData);
      await fetchData();
    } catch (err: any) {
      setLoginError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };"""
        
        login_title = "MP Constituency Dashboard"
        options = """                  <option value="mp_vijayawada@sahayak.gov.in">Vijayawada East (MP)</option>
                  <option value="mp_guntur@sahayak.gov.in">Guntur West (MP)</option>
                  <option value="mp_vizag@sahayak.gov.in">Vizag North (MP)</option>"""
    
    elif login_component_type == "officer":
        old_login = """  // Login officer based on selected persona
  useEffect(() => {
    async function loginAndFetch() {
      setLoading(true);
      try {
        const authData = await api.login(selectedPersona, "password123");
        localStorage.setItem("token", authData.access_token);
        setUser(authData);
        
        // Fetch grievances
        const list = await api.listGrievances();
        setGrievances(list);
      } catch (err) {
        console.error("Auto login failed:", err);
      } finally {
        setLoading(false);
      }
    }
    loginAndFetch();
  }, [selectedPersona]);"""
        
        new_login = """  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLoginError("");
    try {
      const authData = await api.login(selectedPersona, password);
      localStorage.setItem("token", authData.access_token);
      setUser(authData);
      const list = await api.listGrievances();
      setGrievances(list);
    } catch (err: any) {
      setLoginError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };"""
        
        login_title = "Department Officer Dashboard"
        options = """                  <option value="water_officer@sahayak.gov.in">Water Dept Officer</option>
                  <option value="roads_officer@sahayak.gov.in">Roads Dept Officer</option>
                  <option value="sanitation_officer@sahayak.gov.in">Sanitation Officer</option>
                  <option value="electricity_officer@sahayak.gov.in">Electricity Officer</option>"""

    content = content.replace(old_login, new_login)

    # Insert login screen
    login_screen = f"""    if (!user) {{
      return (
        <main className="min-h-screen bg-gray-50 flex items-center justify-center p-4 font-sans text-gray-900">
          <div className="bg-white p-8 rounded-xl shadow-md border border-gray-200 max-w-md w-full">
            <div className="flex flex-col items-center mb-8">
              <div className="p-3 rounded-full bg-blue-50 text-blue-600 mb-3">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={{2}} d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">GovPortal Login</h1>
              <p className="text-sm text-gray-500">{login_title}</p>
            </div>
            
            <form onSubmit={{handleLogin}} className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Select Jurisdiction/Role</label>
                <select
                  value={{selectedPersona}}
                  onChange={{(e) => setSelectedPersona(e.target.value)}}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
{options}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Secure Password</label>
                <input
                  type="password"
                  value={{password}}
                  onChange={{(e) => setPassword(e.target.value)}}
                  className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              {{loginError && <div className="text-red-500 text-sm font-medium">{{loginError}}</div>}}
              
              <button
                type="submit"
                disabled={{loading}}
                className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold tracking-wide transition shadow-sm"
              >
                {{loading ? "Authenticating..." : "Access Dashboard"}}
              </button>
            </form>
          </div>
        </main>
      );
    }}

"""

    content = content.replace('return (\n    <main', login_screen + 'return (\n    <main')

    # Global style replacements
    replacements = {
        'bg-[#090d16] text-white': 'bg-gray-50 text-gray-900',
        'bg-[#0b101d]': 'bg-gray-50',
        'bg-[#070b13]': 'bg-white',
        'bg-gray-900/60': 'bg-white',
        'bg-gray-900/40': 'bg-white',
        'border-white/5': 'border-gray-200',
        'border-white/10': 'border-gray-300',
        'text-gray-400': 'text-gray-500',
        'text-gray-300': 'text-gray-700',
        'text-white': 'text-gray-900',
        'bg-gray-800': 'bg-white border border-gray-200',
        'bg-gray-850': 'bg-white',
        'bg-white/5': 'bg-gray-50',
        'bg-gray-950/60': 'bg-gray-50',
        'text-gradient': 'text-blue-700 font-extrabold',
        'glow-blue': 'shadow-sm',
        'glow-emerald': 'shadow-sm',
        'backdrop-blur': ''
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Apply to MP
process_file('app/mp/page.tsx', 'mp')
# Apply to Officer
process_file('app/officer/page.tsx', 'officer')

print("Update complete")
