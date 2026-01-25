'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  User, 
  Mail, 
  Key, 
  CreditCard, 
  BarChart3, 
  Clock, 
  Loader2,
  Copy,
  Check,
  Plus,
  Trash2,
  Eye,
  EyeOff,
  ArrowUpRight,
  Zap
} from 'lucide-react'

import { useAuth } from '@/components/auth/AuthProvider'
import { createClient } from '@/lib/supabase/client'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

interface UserProfile {
  id: string
  email: string
  full_name: string | null
  subscription_tier: 'free' | 'pro' | 'enterprise'
  credits_balance: number
  daily_research_count: number
  created_at: string
}

interface ApiKey {
  id: string
  name: string
  key_prefix: string
  created_at: string
  last_used_at: string | null
  is_active: boolean
}

interface UsageStats {
  researches_today: number
  researches_total: number
  api_calls_month: number
}

const TIER_LIMITS = {
  free: { research_per_day: 2, label: 'Free', color: 'secondary' as const },
  pro: { research_per_day: 20, label: 'Pro', color: 'default' as const },
  enterprise: { research_per_day: -1, label: 'Enterprise', color: 'default' as const },
}

export default function DashboardPage() {
  const { user, isLoading: authLoading } = useAuth()
  const router = useRouter()
  const supabase = createClient()
  
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [usage, setUsage] = useState<UsageStats>({ researches_today: 0, researches_total: 0, api_calls_month: 0 })
  const [isLoading, setIsLoading] = useState(true)
  
  // API Key creation
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyValue, setNewKeyValue] = useState<string | null>(null)
  const [isCreatingKey, setIsCreatingKey] = useState(false)
  const [showNewKey, setShowNewKey] = useState(false)
  const [copied, setCopied] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/auth/login?redirect=/dashboard')
    }
  }, [user, authLoading, router])

  useEffect(() => {
    if (user) {
      fetchDashboardData()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  const fetchDashboardData = async () => {
    if (!user) return
    
    setIsLoading(true)
    
    try {
      // Fetch user profile
      const { data: profileData } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('id', user.id)
        .single()
      
      if (profileData) {
        setProfile(profileData)
      } else {
        // Create default profile if doesn't exist
        setProfile({
          id: user.id,
          email: user.email || '',
          full_name: null,
          subscription_tier: 'free',
          credits_balance: 10,
          daily_research_count: 0,
          created_at: user.created_at,
        })
      }

      // Fetch API keys
      const { data: keysData } = await supabase
        .from('api_keys')
        .select('id, name, key_prefix, created_at, last_used_at, is_active')
        .eq('user_id', user.id)
        .eq('is_active', true)
        .order('created_at', { ascending: false })
      
      if (keysData) {
        setApiKeys(keysData)
      }

      // Fetch usage stats (simplified - would need actual queries)
      const { count } = await supabase
        .from('research_runs')
        .select('*', { count: 'exact' })
        .eq('user_id', user.id)
      
      setUsage({
        researches_today: profileData?.daily_research_count || 0,
        researches_total: count || 0,
        api_calls_month: 0,
      })
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateApiKey = async () => {
    if (!newKeyName.trim() || !user) return
    
    setIsCreatingKey(true)
    
    try {
      // Generate a new API key (in production, this should be done server-side)
      const keyValue = `drk_${crypto.randomUUID().replace(/-/g, '')}`
      const keyPrefix = keyValue.substring(0, 12)
      
      // Hash the key for storage (simplified - real impl uses SHA-256 on server)
      const { data, error } = await supabase
        .from('api_keys')
        .insert({
          user_id: user.id,
          name: newKeyName.trim(),
          key_prefix: keyPrefix,
          key_hash: keyValue, // In production, this would be hashed server-side
          is_active: true,
        })
        .select()
        .single()
      
      if (error) throw error
      
      setNewKeyValue(keyValue)
      setApiKeys([{ ...data, key_prefix: keyPrefix }, ...apiKeys])
      
    } catch (error) {
      console.error('Error creating API key:', error)
    } finally {
      setIsCreatingKey(false)
    }
  }

  const handleDeleteApiKey = async (keyId: string) => {
    try {
      await supabase
        .from('api_keys')
        .update({ is_active: false })
        .eq('id', keyId)
      
      setApiKeys(apiKeys.filter(k => k.id !== keyId))
    } catch (error) {
      console.error('Error deleting API key:', error)
    }
  }

  const copyToClipboard = async (text: string) => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const resetDialog = () => {
    setNewKeyName('')
    setNewKeyValue(null)
    setShowNewKey(false)
    setDialogOpen(false)
  }

  if (authLoading || isLoading) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!user) return null

  const tier = profile?.subscription_tier || 'free'
  const tierInfo = TIER_LIMITS[tier]
  const dailyLimit = tierInfo.research_per_day
  const dailyUsed = usage.researches_today

  return (
    <div className="container mx-auto max-w-6xl p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="space-y-6"
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">Manage your account and view usage</p>
          </div>
          <Badge variant={tierInfo.color} className="text-sm px-3 py-1">
            {tierInfo.label} Tier
          </Badge>
        </div>

        <Separator />

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Researches Today</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {dailyUsed} {dailyLimit > 0 ? `/ ${dailyLimit}` : ''}
              </div>
              <p className="text-xs text-muted-foreground">
                {dailyLimit > 0 ? `${dailyLimit - dailyUsed} remaining` : 'Unlimited'}
              </p>
              {dailyLimit > 0 && (
                <div className="mt-2 h-2 w-full rounded-full bg-muted">
                  <div 
                    className="h-full rounded-full bg-primary transition-all"
                    style={{ width: `${Math.min((dailyUsed / dailyLimit) * 100, 100)}%` }}
                  />
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Researches</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{usage.researches_total}</div>
              <p className="text-xs text-muted-foreground">All time</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">API Keys</CardTitle>
              <Key className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{apiKeys.length}</div>
              <p className="text-xs text-muted-foreground">Active keys</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Credits</CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{profile?.credits_balance || 0}</div>
              <p className="text-xs text-muted-foreground">Available</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Profile Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Profile
              </CardTitle>
              <CardDescription>Your account information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">{user.email}</span>
              </div>
              {profile?.full_name && (
                <div className="flex items-center gap-3">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">{profile.full_name}</span>
                </div>
              )}
              <div className="flex items-center gap-3">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">
                  Joined {new Date(user.created_at).toLocaleDateString()}
                </span>
              </div>
              <Separator />
              <Button variant="outline" className="w-full" asChild>
                <Link href="/settings">
                  Edit Profile
                  <ArrowUpRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* API Keys Section */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Key className="h-5 w-5" />
                    API Keys
                  </CardTitle>
                  <CardDescription>Manage your API access</CardDescription>
                </div>
                <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                  <DialogTrigger asChild>
                    <Button size="sm" onClick={() => { setNewKeyValue(null); setNewKeyName(''); }}>
                      <Plus className="mr-2 h-4 w-4" />
                      New Key
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>
                        {newKeyValue ? 'API Key Created' : 'Create API Key'}
                      </DialogTitle>
                      <DialogDescription>
                        {newKeyValue 
                          ? 'Copy your key now. You won\'t be able to see it again!'
                          : 'Give your API key a name to help you identify it later.'
                        }
                      </DialogDescription>
                    </DialogHeader>
                    
                    {newKeyValue ? (
                      <div className="space-y-4">
                        <div className="rounded-md bg-muted p-4">
                          <div className="flex items-center justify-between gap-2">
                            <code className="text-sm font-mono break-all">
                              {showNewKey ? newKeyValue : '•'.repeat(40)}
                            </code>
                            <div className="flex gap-1">
                              <Button
                                size="icon"
                                variant="ghost"
                                onClick={() => setShowNewKey(!showNewKey)}
                              >
                                {showNewKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                              </Button>
                              <Button
                                size="icon"
                                variant="ghost"
                                onClick={() => copyToClipboard(newKeyValue)}
                              >
                                {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                              </Button>
                            </div>
                          </div>
                        </div>
                        <DialogFooter>
                          <Button onClick={resetDialog}>Done</Button>
                        </DialogFooter>
                      </div>
                    ) : (
                      <>
                        <div className="space-y-2">
                          <Label htmlFor="keyName">Key Name</Label>
                          <Input
                            id="keyName"
                            placeholder="e.g., Production API Key"
                            value={newKeyName}
                            onChange={(e) => setNewKeyName(e.target.value)}
                          />
                        </div>
                        <DialogFooter>
                          <Button variant="outline" onClick={() => setDialogOpen(false)}>
                            Cancel
                          </Button>
                          <Button 
                            onClick={handleCreateApiKey} 
                            disabled={!newKeyName.trim() || isCreatingKey}
                          >
                            {isCreatingKey ? (
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            ) : null}
                            Create Key
                          </Button>
                        </DialogFooter>
                      </>
                    )}
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              {apiKeys.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No API keys yet. Create one to get started.
                </p>
              ) : (
                <div className="space-y-3">
                  {apiKeys.slice(0, 3).map((key) => (
                    <div 
                      key={key.id} 
                      className="flex items-center justify-between p-3 rounded-md bg-muted"
                    >
                      <div>
                        <p className="text-sm font-medium">{key.name}</p>
                        <p className="text-xs text-muted-foreground font-mono">
                          {key.key_prefix}...
                        </p>
                      </div>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button size="icon" variant="ghost" className="text-destructive hover:text-destructive">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Delete API Key?</AlertDialogTitle>
                            <AlertDialogDescription>
                              This will permanently revoke access for &quot;{key.name}&quot;. 
                              Any applications using this key will stop working.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction 
                              onClick={() => handleDeleteApiKey(key.id)}
                              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            >
                              Delete
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  ))}
                  {apiKeys.length > 3 && (
                    <Button variant="ghost" className="w-full text-sm" asChild>
                      <Link href="/settings/api-keys">
                        View all {apiKeys.length} keys
                        <ArrowUpRight className="ml-2 h-4 w-4" />
                      </Link>
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Upgrade CTA (only for free tier) */}
        {tier === 'free' && (
          <Card className="bg-gradient-to-r from-primary/10 via-primary/5 to-transparent border-primary/20">
            <CardContent className="flex flex-col sm:flex-row items-center justify-between gap-4 p-6">
              <div className="flex items-center gap-4">
                <div className="rounded-full bg-primary/10 p-3">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold">Upgrade to Pro</h3>
                  <p className="text-sm text-muted-foreground">
                    Get 20 researches/day, deeper analysis, priority support, and more.
                  </p>
                </div>
              </div>
              <Button size="lg" className="shrink-0">
                Upgrade Now
                <ArrowUpRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Quick Actions */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Button variant="outline" className="h-auto py-4 justify-start" asChild>
            <Link href="/">
              <div className="flex items-center gap-3">
                <div className="rounded-md bg-primary/10 p-2">
                  <BarChart3 className="h-5 w-5 text-primary" />
                </div>
                <div className="text-left">
                  <p className="font-medium">New Research</p>
                  <p className="text-xs text-muted-foreground">Start a new deep research</p>
                </div>
              </div>
            </Link>
          </Button>
          
          <Button variant="outline" className="h-auto py-4 justify-start" asChild>
            <Link href="/history">
              <div className="flex items-center gap-3">
                <div className="rounded-md bg-primary/10 p-2">
                  <Clock className="h-5 w-5 text-primary" />
                </div>
                <div className="text-left">
                  <p className="font-medium">Research History</p>
                  <p className="text-xs text-muted-foreground">View past researches</p>
                </div>
              </div>
            </Link>
          </Button>
          
          <Button variant="outline" className="h-auto py-4 justify-start" asChild>
            <Link href="/docs/api">
              <div className="flex items-center gap-3">
                <div className="rounded-md bg-primary/10 p-2">
                  <Key className="h-5 w-5 text-primary" />
                </div>
                <div className="text-left">
                  <p className="font-medium">API Documentation</p>
                  <p className="text-xs text-muted-foreground">Integrate with your apps</p>
                </div>
              </div>
            </Link>
          </Button>
        </div>
      </motion.div>
    </div>
  )
}
