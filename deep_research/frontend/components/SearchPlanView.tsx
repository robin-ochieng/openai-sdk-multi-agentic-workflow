'use client'

import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { WebSearchPlan } from '@/lib/types'
import { Search, CheckCircle2 } from 'lucide-react'

interface SearchPlanViewProps {
  searchPlan: WebSearchPlan
}

export function SearchPlanView({ searchPlan }: SearchPlanViewProps) {
  return (
    <Card className="overflow-hidden border-2 border-blue-500/20 bg-gradient-to-br from-card to-card/80">
      <div className="border-b border-border/50 bg-gradient-to-r from-blue-500/10 to-blue-500/5 p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/20">
            <Search className="h-6 w-6 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold">Search Plan Created</h2>
            <p className="text-sm text-muted-foreground">
              {searchPlan.searches.length} strategic searches planned
            </p>
          </div>
          <Badge variant="secondary" className="h-fit">
            <CheckCircle2 className="mr-1 h-3 w-3" />
            Ready
          </Badge>
        </div>
      </div>

      <div className="p-6">
        <Accordion type="single" collapsible defaultValue="item-0">
          {searchPlan.searches.map((search, index) => (
            <AccordionItem key={index} value={`item-${index}`}>
              <AccordionTrigger className="hover:no-underline">
                <div className="flex items-center gap-3 text-left">
                  <Badge variant="outline" className="h-6 w-6 justify-center p-0">
                    {index + 1}
                  </Badge>
                  <span className="font-medium">{search.query}</span>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-3 pl-9 pt-2">
                  <div>
                    <h4 className="mb-1 text-sm font-semibold text-muted-foreground">
                      Purpose
                    </h4>
                    <p className="text-sm">{search.purpose}</p>
                  </div>
                  {search.focus_areas && search.focus_areas.length > 0 && (
                    <div>
                      <h4 className="mb-2 text-sm font-semibold text-muted-foreground">
                        Focus Areas
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {search.focus_areas.map((area, i) => (
                          <Badge key={i} variant="secondary">
                            {area}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </Card>
  )
}
