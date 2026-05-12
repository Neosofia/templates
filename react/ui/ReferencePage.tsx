import { useState } from 'react';
import { useForm } from '@tanstack/react-form';
import * as z from 'zod';
import { Button } from './src/components/ui/button';
import { Badge } from './src/components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from './src/components/ui/card';
import { Alert, AlertTitle, AlertDescription } from './src/components/ui/alert';
import { Input } from './src/components/ui/input';
import { Textarea } from './src/components/ui/textarea';
import { Field, FieldLabel, FieldGroup } from './src/components/ui/field';
import { Separator } from './src/components/ui/separator';
import { Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator, BreadcrumbPage } from './src/components/ui/breadcrumb';
import { NavigationMenu, NavigationMenuList, NavigationMenuItem, NavigationMenuTrigger, NavigationMenuContent, NavigationMenuLink } from './src/components/ui/navigation-menu';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuGroup } from './src/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from './src/components/ui/avatar';
import { Label } from './src/components/ui/label';
import { Sheet, SheetTrigger, SheetClose, SheetContent, SheetHeader, SheetFooter, SheetTitle, SheetDescription } from './src/components/ui/sheet';

const configSchema = z.object({
  email: z.string().email('Please enter a valid email address.'),
  notes: z.string(),
});

export default function ReferencePage() {
  const [submitted, setSubmitted] = useState(false);
  const form = useForm({
    defaultValues: { email: '', notes: '' },
    validators: { onSubmit: configSchema },
    onSubmit: () => { setSubmitted(true); form.reset(); },
  });

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col overflow-x-hidden">
      {/* Global Header Integration */}
      <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur supports-[backdrop-filter]:bg-slate-950/60">
        <div className="mx-auto w-full flex h-16 max-w-5xl items-center px-8 justify-between">
          <div className="mr-8 font-bold text-slate-100 tracking-tight">Neosofia</div>
          <div className="flex items-center gap-6">
            <NavigationMenu viewport={false}>
              <NavigationMenuList>
                <NavigationMenuItem>
                  <NavigationMenuTrigger>Dashboard</NavigationMenuTrigger>
                  <NavigationMenuContent className="min-w-[800px] p-4 bg-slate-950 border-slate-800 text-slate-200">
                    <div className="grid gap-3">
                      <NavigationMenuLink asChild>
                        <a href="#" className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-slate-800 hover:text-slate-100 focus:bg-slate-800 focus:text-slate-100">
                          <div className="text-sm font-medium leading-none text-slate-200">Analytics</div>
                          <p className="line-clamp-2 text-sm leading-snug text-slate-400">Review platform metrics.</p>
                        </a>
                      </NavigationMenuLink>
                    </div>
                  </NavigationMenuContent>
                </NavigationMenuItem>
                <NavigationMenuItem>
                  <NavigationMenuTrigger>Components</NavigationMenuTrigger>
                </NavigationMenuItem>
              </NavigationMenuList>
            </NavigationMenu>
            <DropdownMenu modal={false}>
              <DropdownMenuTrigger className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-slate-800 transition-colors outline-none">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-[#0D4884] text-slate-100 font-semibold text-xs">
                      JS
                    </AvatarFallback>
                  </Avatar>
                  <div className="hidden sm:flex sm:flex-col sm:items-start sm:text-left gap-0.5 whitespace-nowrap">
                    <span className="text-sm font-semibold text-slate-100 leading-none">
                      Jane Smith
                    </span>
                    <span className="text-[11px] text-slate-400 leading-none">
                      Neosofia Inc.
                    </span>
                  </div>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-64 mt-1 bg-slate-950 border border-slate-800 text-slate-300 shadow-2xl shadow-black/40 rounded-2xl" align="end">
                <DropdownMenuGroup>
                  <DropdownMenuLabel className="font-normal flex flex-col space-y-1 p-2">
                    <span className="text-sm font-semibold leading-none text-slate-100">Jane Smith</span>
                    <span className="text-xs text-slate-400 leading-none mt-0.5">jane.smith@neosofia.com</span>
                    <span className="text-xs text-slate-400 leading-none mt-1">Active role: <span className="text-slate-100">Admin</span></span>
                  </DropdownMenuLabel>
                </DropdownMenuGroup>

                <DropdownMenuSeparator className="bg-slate-800" />

                <div className="px-3 py-2 flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                    <span>Organization</span>
                  </div>
                  <span className="text-xs text-slate-300 truncate max-w-30">Neosofia Inc.</span>
                </div>

                <DropdownMenuSeparator className="bg-slate-800" />

                <DropdownMenuGroup>
                  <DropdownMenuItem className="focus:bg-slate-800 focus:text-slate-100 cursor-pointer rounded-lg px-2 py-2 text-sm">
                    Profile
                  </DropdownMenuItem>
                  <DropdownMenuItem className="focus:bg-slate-800 focus:text-slate-100 cursor-pointer rounded-lg px-2 py-2 text-sm">
                    Settings
                  </DropdownMenuItem>
                </DropdownMenuGroup>

                <DropdownMenuSeparator className="bg-slate-800" />
                <DropdownMenuItem className="cursor-pointer text-red-400 focus:text-red-300 focus:bg-red-950/50 rounded-lg px-2 py-2 text-sm">
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Main Layout Integration */}
      <main className="flex-1 w-full max-w-5xl mx-auto p-8 space-y-16">
        <div className="space-y-6">
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/">Home</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbLink href="/components">Components</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>Reference</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          
          <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-5 mt-2">
            <p className="text-sm text-slate-400 leading-relaxed">
              <strong className="text-slate-200">Layout Notes:</strong> The global header is fixed to the top edge (<code>sticky top-0</code>, <code>h-16</code>) with a subtle bottom border and backdrop blur to maintain hierarchy while scrolling. The navigation menu aligns horizontally with the brand mark using standard flexbox centering. Breadcrumbs sit directly inside the main content container, isolated immediately above the primary page title with a <code>space-y-6</code> gap, providing structural context without crowding the header.
            </p>
          </div>

          <div className="space-y-4 pt-4">
            <h1 className="text-4xl font-bold text-slate-100 tracking-tight">Neosofia Design Reference</h1>
            <p className="text-lg text-slate-400">
              This document serves as the foundational reference for Neosofia UI components. 
              Use these elements to maintain consistent design intent, interaction patterns, and visual hierarchy across all applications.
            </p>
          </div>
        </div>

      {/* Buttons */}
      <section className="space-y-6">
        <div className="space-y-2 border-b pb-4">
          <h2 className="text-2xl font-semibold tracking-tight">Buttons</h2>
          <p className="text-muted-foreground">
            Buttons communicate actions that users can take. They should be clear, predictable, and follow a strict visual hierarchy.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <CardTitle>Variants</CardTitle>
              <CardDescription>Primary actions should use default. Secondary and outline variants are for alternative actions. Destructive actions must be clearly marked.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-4">
              <Button>Primary Action</Button>
              <Button variant="secondary">Secondary Action</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost Style</Button>
              <Button variant="destructive">Destructive</Button>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Badges */}
      <section className="space-y-6">
        <div className="space-y-2 border-b pb-4">
          <h2 className="text-2xl font-semibold tracking-tight">Badges</h2>
          <p className="text-muted-foreground">
            Badges are used to highlight status, statuses, or categorize items. They are generally non-interactive.
          </p>
        </div>
        <div className="flex flex-wrap gap-4">
          <Badge>Active</Badge>
          <Badge variant="secondary">Draft</Badge>
          <Badge variant="destructive">Failed</Badge>
          <Badge variant="outline">Archived</Badge>
        </div>
      </section>

      {/* Labels */}
      <section className="space-y-6">
        <div className="space-y-2 border-b pb-4">
          <h2 className="text-2xl font-semibold tracking-tight">Labels</h2>
          <p className="text-muted-foreground">
            Labels connect form controls with accessible text and improve field discoverability.
          </p>
        </div>
        <div className="space-y-2 max-w-md">
          <Label htmlFor="label-example" className="block">Example label</Label>
          <Input id="label-example" placeholder="Label-connected input" />
        </div>
      </section>

      {/* Sheets */}
      <section className="space-y-6">
        <div className="space-y-2 border-b pb-4">
          <h2 className="text-2xl font-semibold tracking-tight">Sheet</h2>
          <p className="text-muted-foreground">
            Sheets are slide-over panels for secondary actions, settings, or contextual content.
          </p>
        </div>
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="secondary">Open Sheet</Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-full max-w-md bg-slate-900 border-slate-800 text-slate-100">
            <SheetHeader>
              <SheetTitle>Reference sheet</SheetTitle>
              <SheetDescription>Use sheets for supplemental content without leaving the current page.</SheetDescription>
            </SheetHeader>
            <div className="px-4 space-y-4 text-sm text-slate-300">
              <p>This is a live sheet example inside the reference UI.</p>
              <p>Sheets are useful for details, quick forms, and secondary workflows.</p>
            </div>
            <SheetFooter>
              <SheetClose asChild>
                <Button className="w-full">Close Panel</Button>
              </SheetClose>
            </SheetFooter>
          </SheetContent>
        </Sheet>
      </section>

      {/* Forms & Inputs */}
      <section className="space-y-6">
        <div className="space-y-2 border-b pb-4">
          <h2 className="text-2xl font-semibold tracking-tight">Forms & User Input</h2>
          <p className="text-muted-foreground">
            Forms structure data collection. Always use the Field component to wrap labels, inputs, descriptions, and errors together for maximum accessibility and consistent layout.
          </p>
        </div>
        <Card className="max-w-2xl">
          <CardHeader>
            <CardTitle>Standard Form Layout</CardTitle>
            <CardDescription>Submit with an invalid email to see inline validation errors.</CardDescription>
          </CardHeader>
          <CardContent>
            {submitted && (
              <Alert className="mb-4 border-green-800 bg-green-950/40 text-green-300">
                <AlertTitle className="text-green-200">Email sent</AlertTitle>
                <AlertDescription>Thanks — your message has been received.</AlertDescription>
              </Alert>
            )}
            <form onSubmit={(e) => { e.preventDefault(); setSubmitted(false); form.handleSubmit(); }}>
              <FieldGroup>
                <form.Field name="email">
                  {(field) => {
                    const isInvalid = (field.state.meta.isTouched || form.state.isSubmitted) && field.state.meta.errors.length > 0;
                    return (
                      <Field>
                        <FieldLabel htmlFor={field.name}>
                          Email Address
                          {isInvalid && field.state.meta.errors[0]?.message && (
                            <span className="ml-1 font-normal text-red-400">({field.state.meta.errors[0].message})</span>
                          )}
                        </FieldLabel>
                        <Input
                          id={field.name}
                          name={field.name}
                          type="text"
                          value={field.state.value}
                          onChange={(e) => field.handleChange(e.target.value)}
                          onBlur={field.handleBlur}
                          placeholder="example@neosofia.tech"
                        />
                      </Field>
                    );
                  }}
                </form.Field>
                <form.Field name="notes">
                  {(field) => (
                    <Field>
                      <FieldLabel htmlFor={field.name}>System Notes</FieldLabel>
                      <Textarea
                        id={field.name}
                        name={field.name}
                        value={field.state.value}
                        onChange={(e) => field.handleChange(e.target.value)}
                        onBlur={field.handleBlur}
                        placeholder="Provide any additional context here..."
                      />
                    </Field>
                  )}
                </form.Field>
                <Button type="submit" className="w-fit">Save Configuration</Button>
              </FieldGroup>
            </form>
          </CardContent>
        </Card>
      </section>

      {/* Alerts */}
      <section className="space-y-6">
        <div className="space-y-2 border-b pb-4">
          <h2 className="text-2xl font-semibold tracking-tight">Alerts</h2>
          <p className="text-muted-foreground">
            Alerts communicate important system-level feedback, warnings, or errors. They interrupt the flow but embed directly in the layout.
          </p>
        </div>
        <div className="grid gap-4 max-w-2xl">
          <Alert>
            <AlertTitle>System Update</AlertTitle>
            <AlertDescription>
              A new version of the Neosofia SDK is available. Please update your dependencies.
            </AlertDescription>
          </Alert>
          <Alert variant="destructive">
            <AlertTitle>Connection Error</AlertTitle>
            <AlertDescription>
              Failed to connect to the Authentication service. Ensure your local stack is running.
            </AlertDescription>
          </Alert>
        </div>
      </section>

      <Separator className="my-8" />
      <p className="text-sm text-center text-muted-foreground">
        Templates &copy; {new Date().getFullYear()} Neosofia
      </p>
      </main>
    </div>
  );
}
