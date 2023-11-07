package com.moneydance.modules.features.moneyPie;


import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Image;
import java.awt.LayoutManager;
import java.awt.Point;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseMotionAdapter;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;

import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JButton;
import javax.swing.JTextPane;

@SuppressWarnings("serial")
public class BudgetSplash extends JDialog{
	private String title;
	private int build;
	private JPanel contentPane;
	private JPanel main;
	private JTextPane textPane;
	private Point initialClick;
	private JLabel closeLabel;
	private JPanel closePanel;
	
	private ImageIcon closeNormal;
	private ImageIcon closeHover;
	private ImageIcon closePress;
	
	public BudgetSplash( String title, int build ){
		this( null, title, build );
		
	}
	
	public BudgetSplash( JFrame frame, String title, int build ) {
		super( frame, title );
		
		this.title = title;
		this.build = build;
		
		setTitle( title );
		initialize();
		showWindow();
		addContent();
		installListeners();
	}
	
	public void addContent(){
		this.setSize( new Dimension( 300, 250 ) );
		
		textPane = new JTextPane(); // creates an empty text pane
        textPane.setContentType("text/html"); // lets Java know it will be HTML                  
        textPane.setText("<h1>"+title+" <small>build "+build+"</small></h1>" +
                         "<p>This extension is provided with no limitation and at no cost by the <b>Raging Coders</b>.<br/><br/>Send all questions and comments to <a href='mailto:support@ragingcoders.com'>support@ragingcoders.com</a><br/></p>" +
                         "<p>A lot of hard work goes into this, please consider a small donation to feed our coders.</p>");
        textPane.setPreferredSize(new Dimension(280,180));
        textPane.setBackground(new Color(0,0,0,0));
        
        ImageIcon donateIcon = new ImageIcon(getImage("/com/moneydance/modules/features/moneyPie/images/donate.gif"));
        JButton payButton = new JButton(donateIcon);
        payButton.setBorderPainted(false);
        payButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
            	openPayPal();
            }
        }); 

        this.getContentPane().add(textPane);
        this.getContentPane().add(payButton);
        
	}
	
	public void openPayPal(){
		java.awt.Desktop desktop = java.awt.Desktop.getDesktop();
		try {
			 
            java.net.URI uri = new java.net.URI( "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=CQ8MFVKRZJADG" );
            desktop.browse( uri );
            this.close();
        }
        catch ( Exception e ) {
            System.err.println( e.getMessage() );
        }
	}
	
	public void openMailTo(){
		java.awt.Desktop desktop = java.awt.Desktop.getDesktop();
		try {
			 
            java.net.URI uri = new java.net.URI( "mailto:support@ragingcoders.com" );
            desktop.browse( uri );
            this.close();
        }
        catch ( Exception e ) {
            System.err.println( e.getMessage() );
        }
	}
	
	private void initialize()
	{
		setUndecorated( true );
		contentPane = new JPanel();
        
		setContentPane( contentPane );
		
		
		if ( main == null )
		{
			main = new JPanel();
		}
        
		closePanel = new JPanel( new BorderLayout() );
		initialClick = new Point();
	}
	
	public JPanel getContentPane()
	{
		return main;
	}
	
	public void setLayout( LayoutManager manager )
	{
		if ( main == null  )
		{
			main = new JPanel();
			main.setLayout( new FlowLayout() );
		}
		else
		{
			main.setLayout( manager );
		}
		
		if ( !(getLayout() instanceof BorderLayout) )
		{
			super.setRootPaneCheckingEnabled( false );
			super.setLayout( new BorderLayout() );
			super.setRootPane( super.getRootPane() );
			super.setRootPaneCheckingEnabled( true );
		}
	}

	/**
	 * Sets the background color of the Frame and all panels
	 * 
	 */
	public void setBackground( Color color )
	{
		super.setBackground( color );
		
		if ( contentPane != null )
		{
			contentPane.setBackground( color );
			closePanel.setBackground( color );
			main.setBackground( color );
		}
	}
	
	/**
	 * Add a Component to the main content Panel
	 */
	public Component add( Component comp )
	{
		return main.add( comp );
	}
	
	private Image getImage(String urlName) {

        try {
            InputStream inputStream = getClass().getResourceAsStream(urlName);
            
            if (inputStream != null) {
                ByteArrayOutputStream outputStream = new ByteArrayOutputStream(1000);
                byte buffer[] = new byte[1024];
                int count;
                while ((count = inputStream.read(buffer, 0, buffer.length)) >= 0) {
                    outputStream.write(buffer, 0, count);
                }
                
                return Toolkit.getDefaultToolkit().createImage(outputStream.toByteArray());
            }
            
        } catch (IOException error) {
            error.printStackTrace();
        }
        
        return null;
        
    }
	
	private void showWindow()
	{
		// If not set, default to FlowLayout
		if ( main.getLayout() == null )
		{
			setLayout( new FlowLayout() );
		}
		
		closeNormal = new ImageIcon(getImage("/com/moneydance/modules/features/moneyPie/images/close.gif"));
		closeHover  = new ImageIcon(getImage("/com/moneydance/modules/features/moneyPie/images/close_hov.gif"));
		closePress  = new ImageIcon(getImage("/com/moneydance/modules/features/moneyPie/images/close_press.gif"));
		closeLabel  = new JLabel( closeNormal );
		
		// Put the label with the image on the far right
		closePanel.add( closeLabel, BorderLayout.EAST );
		
		// Add the two panels to the content pane
		contentPane.setLayout( new BorderLayout() );
		contentPane.add( closePanel, BorderLayout.NORTH );
		contentPane.add( main, BorderLayout.CENTER );
		
		// set raised beveled border for window
		contentPane.setBorder( 
				BorderFactory.createRaisedBevelBorder() );

		// Set position somewhere near the middle of the screen
		Dimension screenSize = 
			Toolkit.getDefaultToolkit().getScreenSize();
		setLocation( screenSize.width / 2 - ( getWidth()/ 2 ),
                   screenSize.height / 2 - ( getHeight() / 2 ) );
		
		// keep window on top of others
		setAlwaysOnTop( true );
	}
	
	/* 
	 * Add all listeners
	 */
	private void installListeners()
	{
		// Get point of initial mouse click
		addMouseListener( new MouseAdapter()
		{
			public void mousePressed( MouseEvent e )
			{
				initialClick = e.getPoint();
				getComponentAt( initialClick );
				
			}
		});
		
		// Move window when mouse is dragged
		addMouseMotionListener( new MouseMotionAdapter()
		{
			public void mouseDragged( MouseEvent e )
			{
				// get location of Window
				int thisX = getLocation().x;
				int thisY = getLocation().y;
				
				// Determine how much the mouse moved since the initial click
				int xMoved = 
					( thisX + e.getX() ) - ( thisX + initialClick.x );
				int yMoved = 
					( thisY + e.getY() ) - ( thisY + initialClick.y );
				
				// Move window to this position
				int X = thisX + xMoved;
				int Y = thisY + yMoved;
				setLocation( X, Y );
			}
		});
		
		textPane.addMouseListener( new MouseAdapter() 
		{
			public void mousePressed( MouseEvent e )
			{
				JTextPane editor = (JTextPane) e.getSource();
				Point pt = new Point(e.getX(), e.getY());
			    int pos = editor.viewToModel(pt);
			    if (pos >= 0) {

			    }
				openMailTo();
			}
		});
		
		// Close "button" (image) listeners
		closeLabel.addMouseListener( new MouseAdapter()
		{
			public void mousePressed( MouseEvent e )
			{
				closeLabel.setIcon( closePress );
			}
			
			public void mouseReleased( MouseEvent e )
			{
				closeLabel.setIcon( closeNormal );
			}
			
			public void mouseEntered( MouseEvent e )
			{
				closeLabel.setIcon( closeHover );
			}
			
			public void mouseExited( MouseEvent e )
			{
				closeLabel.setIcon( closeNormal );
			}
			
			public void mouseClicked( MouseEvent e )
			{
				
				close();
			}
		});
	}

	// close and dispose
	public void close()
	{
		setVisible( false );
		dispose();
	}

}
