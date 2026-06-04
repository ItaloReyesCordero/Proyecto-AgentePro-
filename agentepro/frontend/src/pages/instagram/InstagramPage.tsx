import { Instagram, Loader2, Sparkles, Check, X, Heart, MessageCircle } from 'lucide-react'
import { useInstagramPosts, useGeneratePost, useApprovePost, useRejectPost } from '../../hooks/useInstagram'
import { StatusBadge } from '../../components/common/StatusBadge'
import { EmptyState } from '../../components/common/EmptyState'
import type { InstagramPost } from '../../types/instagram'

export function InstagramPage() {
  const { data, isLoading } = useInstagramPosts()
  const generate = useGeneratePost()
  const posts = data?.items ?? []

  function handleGenerate() {
    generate.mutate({ week_start: new Date().toISOString().slice(0, 10), count: 3 })
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-heading text-xl font-bold text-text-primary">Instagram</h2>
          <p className="text-sm text-text-secondary">Posts generados con IA</p>
        </div>
        <button onClick={handleGenerate} disabled={generate.isPending} className="btn-primary">
          {generate.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="h-4 w-4" />
          )}
          Generar posts de la semana
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
        </div>
      ) : posts.length === 0 ? (
        <EmptyState
          icon={Instagram}
          title="Sin posts"
          description="Genera tu primera tanda de posts con IA."
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  )
}

function PostCard({ post }: { post: InstagramPost }) {
  const approve = useApprovePost()
  const reject = useRejectPost()
  const pending = post.status === 'pending_approval'

  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-card">
      {post.image_url ? (
        <img src={post.image_url} alt="" className="aspect-square w-full object-cover" />
      ) : (
        <div className="flex aspect-square w-full items-center justify-center bg-text-primary/5">
          <Instagram className="h-10 w-10 text-text-secondary" />
        </div>
      )}
      <div className="space-y-2 p-4">
        <div className="flex items-center justify-between">
          <StatusBadge status={post.status} />
          {post.status === 'published' && (
            <div className="flex items-center gap-3 text-xs text-text-secondary">
              <span className="flex items-center gap-1">
                <Heart className="h-3 w-3" /> {post.likes_count}
              </span>
              <span className="flex items-center gap-1">
                <MessageCircle className="h-3 w-3" /> {post.comments_count}
              </span>
            </div>
          )}
        </div>
        <p className="line-clamp-3 text-sm text-text-secondary">{post.caption}</p>
        {post.hashtags.length > 0 && (
          <p className="text-xs text-secondary">{post.hashtags.slice(0, 5).join(' ')}</p>
        )}
        {pending && (
          <div className="flex gap-2 pt-1">
            <button
              onClick={() => approve.mutate({ id: post.id })}
              className="flex flex-1 items-center justify-center gap-1 rounded-lg bg-primary py-1.5 text-sm font-medium text-white hover:bg-primary/90"
            >
              <Check className="h-4 w-4" /> Aprobar
            </button>
            <button
              onClick={() => reject.mutate(post.id)}
              className="flex flex-1 items-center justify-center gap-1 rounded-lg border border-border py-1.5 text-sm font-medium text-text-secondary hover:bg-text-primary/5"
            >
              <X className="h-4 w-4" /> Rechazar
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
